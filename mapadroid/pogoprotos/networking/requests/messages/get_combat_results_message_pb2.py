# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pogoprotos/networking/requests/messages/get_combat_results_message.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='pogoprotos/networking/requests/messages/get_combat_results_message.proto',
  package='pogoprotos.networking.requests.messages',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=b'\nHpogoprotos/networking/requests/messages/get_combat_results_message.proto\x12\'pogoprotos.networking.requests.messages\",\n\x17GetCombatResultsMessage\x12\x11\n\tcombat_id\x18\x01 \x01(\tb\x06proto3'
)




_GETCOMBATRESULTSMESSAGE = _descriptor.Descriptor(
  name='GetCombatResultsMessage',
  full_name='pogoprotos.networking.requests.messages.GetCombatResultsMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='combat_id', full_name='pogoprotos.networking.requests.messages.GetCombatResultsMessage.combat_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=117,
  serialized_end=161,
)

DESCRIPTOR.message_types_by_name['GetCombatResultsMessage'] = _GETCOMBATRESULTSMESSAGE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

GetCombatResultsMessage = _reflection.GeneratedProtocolMessageType('GetCombatResultsMessage', (_message.Message,), {
  'DESCRIPTOR' : _GETCOMBATRESULTSMESSAGE,
  '__module__' : 'pogoprotos.networking.requests.messages.get_combat_results_message_pb2'
  # @@protoc_insertion_point(class_scope:pogoprotos.networking.requests.messages.GetCombatResultsMessage)
  })
_sym_db.RegisterMessage(GetCombatResultsMessage)


# @@protoc_insertion_point(module_scope)