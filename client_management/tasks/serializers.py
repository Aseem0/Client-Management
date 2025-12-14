from rest_framework import serializers
from .models import Task, TaskGroup
from django.contrib.auth import get_user_model

User = get_user_model()

class TaskGroupSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    created_by = serializers.ReadOnlyField(source='created_by.id')

    class Meta:
        model = TaskGroup
        fields = ['id', 'name', 'members', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        request = self.context.get('request')
        created_by = getattr(request, 'user', None)
        
        validated_data.pop('created_by', None)

        group = TaskGroup.objects.create(created_by=created_by, **validated_data)
        
        if members:
            group.members.set(members)
        return group

    def update(self, instance, validated_data):
        members = validated_data.pop('members', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if members is not None:
            instance.members.set(members)
        return instance


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    group = serializers.PrimaryKeyRelatedField(queryset=TaskGroup.objects.all(), required=False, allow_null=True)
    created_by = serializers.ReadOnlyField(source='created_by.id')
    due_date = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"], required=False, allow_null=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assigned_to', 'group',
            'status', 'due_date', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def validate_assigned_to(self, value):
        for u in value:
            if getattr(u, 'role', None) != 'employee':
                raise serializers.ValidationError(f"User {u.id} ({u.username}) is not an employee and cannot be assigned tasks.")
        return value

    def validate(self, data):
        # For updates, include existing assignments if missing
        assigned_to = data.get('assigned_to')
        group = data.get('group')

        if self.instance:  # PATCH/PUT
            if assigned_to is None:
                assigned_to = self.instance.assigned_to.all()
            if group is None:
                group = self.instance.group

        if (not assigned_to or len(assigned_to) == 0) and group is None:
            raise serializers.ValidationError("Task must be assigned to at least one user or a group.")

        return data

    def create(self, validated_data):
        assigned_users = validated_data.pop('assigned_to', [])
        group = validated_data.pop('group', None)
        request = self.context.get('request', None)
        created_by = getattr(request, 'user', None)
        task = Task.objects.create(created_by=created_by, group=group, **validated_data)

        # Assign users from group + assigned_to
        members = set()
        if group:
            members.update(group.members.all())
        if assigned_users:
            members.update(assigned_users)
        if members:
            task.assigned_to.set(list(members))

        return task

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        # Employee: can only update status
        if getattr(user, 'role', None) == 'employee':
            instance.status = validated_data.get('status', instance.status)
            instance.save()
            return instance

        # Admin/Manager: full update
        assigned_users = validated_data.pop('assigned_to', None)
        group = validated_data.pop('group', None)

        for attr, val in validated_data.items():
            setattr(instance, attr, val)

        instance.group = group
        instance.save()

        # Update assigned_to
        if assigned_users is not None:
            instance.assigned_to.set(assigned_users)
        elif group is not None:
            instance.assigned_to.set(group.members.all())

        return instance