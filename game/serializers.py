from django.utils.translation import gettext_lazy as _
from .consumers import Maze, MazeConsumer
from rest_framework import serializers


class MessageSerializer:
    def __init__(self, event, content):
        self.event = event
        self.content = content


class MazeMessageSerializer(serializers.Serializer):
    """Serialize for validation WS messages

    In project serializer use only for client messages,
    but server messages also can use for this serializer (need add validation)

    """
    class Meta:
        fields = ('event', 'content')

    EVENTS = (
        MazeConsumer.TIMER_EVENT,
        MazeConsumer.NEW_MAZE_EVENT,
        MazeConsumer.NEW_COORD_EVENT,
        MazeConsumer.GAME_OVER_EVENT,
        MazeConsumer.ERROR_EVENT,
        MazeConsumer.MOVE_EVENT,
        MazeConsumer.NAME_EVENT,
    )
    PATHS = (
        Maze.RIGHT,
        Maze.LEFT,
        Maze.TOP,
        Maze.BOTTOM,
    )

    event = serializers.ChoiceField(choices=EVENTS,
                                    error_messages={'invalid_choice': _(f'Bad event key. Must one from: {EVENTS}'),
                                                    'required': _("'event' key is required"),
                                                    }
                                    )
    content = serializers.CharField(required=True, error_messages={'required': _("'content' key is required")})

    def validate(self, attrs):
        attrs = super(MazeMessageSerializer, self).validate(attrs)

        if attrs['event'] == MazeConsumer.MOVE_EVENT:
            if self.context.get('status') != MazeConsumer.WAIT_MOVE_STATUS:
                raise serializers.ValidationError(_('Server not receive message for move.'),
                                                  code='bad event')
            if attrs['content'] not in MazeMessageSerializer.PATHS:
                raise serializers.ValidationError(_(f"Bad path. Must one from: {MazeMessageSerializer.PATHS}"),
                                                  code='bad path')

        if attrs['event'] == MazeConsumer.NAME_EVENT:
            if self.context.get('status') != MazeConsumer.WAIT_NAME_STATUS:
                raise serializers.ValidationError(_('Server not receive message for set name.'),
                                                  code='bad event')
            if not attrs['content'] or len(attrs['content']) > 20:
                raise serializers.ValidationError(_(f"Length name must be less 20 and more 0."),
                                                  code='bad name')

        return attrs

    def update(self, instance, validated_data):
        instance.event = validated_data.get('event', instance.event)
        instance.content = validated_data.get('content', instance.content)
        return instance

    def create(self, validated_data):
        return MessageSerializer(**validated_data)
