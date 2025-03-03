from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union

class User(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone_number: Optional[str] = None
    status: Optional[Dict[str, Any]] = None
    profile_photo: Optional[Dict[str, Any]] = None
    is_contact: Optional[bool] = None
    is_mutual_contact: Optional[bool] = None
    is_verified: Optional[bool] = None
    restriction_reason: Optional[str] = None
    is_scam: Optional[bool] = None
    is_fake: Optional[bool] = None
    have_access: Optional[bool] = None

class UserResponse(BaseModel):
    success: bool
    user: Optional[User] = None
    error: Optional[str] = None

class Chat(BaseModel):
    id: int
    type: Dict[str, Any]
    title: str
    photo: Optional[Dict[str, Any]] = None
    permissions: Optional[Dict[str, Any]] = None
    last_message: Optional[Dict[str, Any]] = None
    positions: Optional[List[Dict[str, Any]]] = None
    is_marked_as_unread: Optional[bool] = None
    is_blocked: Optional[bool] = None
    has_scheduled_messages: Optional[bool] = None
    can_be_deleted_only_for_self: Optional[bool] = None
    can_be_deleted_for_all_users: Optional[bool] = None
    can_be_reported: Optional[bool] = None
    default_disable_notification: Optional[bool] = None
    unread_count: Optional[int] = None
    last_read_inbox_message_id: Optional[int] = None
    last_read_outbox_message_id: Optional[int] = None
    unread_mention_count: Optional[int] = None
    notification_settings: Optional[Dict[str, Any]] = None
    message_ttl: Optional[int] = None
    theme_name: Optional[str] = None
    action_bar: Optional[Dict[str, Any]] = None
    video_chat: Optional[Dict[str, Any]] = None
    pending_join_requests: Optional[Dict[str, Any]] = None
    reply_markup_message_id: Optional[int] = None
    client_data: Optional[str] = None

class ChatListResponse(BaseModel):
    success: bool
    total_count: int
    chats: List[int]

class Message(BaseModel):
    id: int
    sender_id: Dict[str, Any]
    chat_id: int
    content: Dict[str, Any]
    date: int
    edit_date: Optional[int] = None
    reply_to_message_id: Optional[int] = None
    reply_markup: Optional[Dict[str, Any]] = None
    is_outgoing: Optional[bool] = None
    can_be_edited: Optional[bool] = None
    can_be_forwarded: Optional[bool] = None
    can_be_deleted_only_for_self: Optional[bool] = None
    can_be_deleted_for_all_users: Optional[bool] = None
    can_get_statistics: Optional[bool] = None
    can_get_message_thread: Optional[bool] = None
    is_channel_post: Optional[bool] = None
    contains_unread_mention: Optional[bool] = None
    date_read: Optional[int] = None
    auto_delete_in: Optional[int] = None
    via_bot_user_id: Optional[int] = None
    author_signature: Optional[str] = None
    media_album_id: Optional[int] = None
    restriction_reason: Optional[str] = None
    interaction_info: Optional[Dict[str, Any]] = None
    scheduling_state: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    success: bool
    message: Optional[Message] = None
    error: Optional[str] = None

class MessagesResponse(BaseModel):
    success: bool
    messages: List[Message]
    total_count: int
    
class ErrorResponse(BaseModel):
    success: bool = False
    error: str

class LoginRequest(BaseModel):
    phone: str = Field(..., description="Número de telefone no formato internacional (ex: +5511999999999)")
    
class CodeVerificationRequest(BaseModel):
    code: str = Field(..., description="Código de verificação recebido por SMS ou Telegram")
    
class PasswordVerificationRequest(BaseModel):
    password: str = Field(..., description="Senha da conta Telegram") 