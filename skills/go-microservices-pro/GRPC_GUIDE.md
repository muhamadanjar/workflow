# gRPC Implementation Guide

## Proto Definition

```protobuf
syntax = "proto3";

package user.v1;

message User {
    string id = 1;
    string name = 2;
    string email = 3;
}

message GetUserRequest {
    string user_id = 1;
}

message GetUserResponse {
    User user = 1;
}

service UserService {
    rpc GetUser(GetUserRequest) returns (GetUserResponse);
    rpc ListUsers(Empty) returns (stream User);
}
```

## Server Implementation

```go
type UserServer struct {
    repo UserRepository
}

func (s *UserServer) GetUser(ctx context.Context, 
    req *pb.GetUserRequest) (*pb.GetUserResponse, error) {
    
    user, err := s.repo.GetByID(ctx, req.UserId)
    if err != nil {
        return nil, status.Errorf(codes.NotFound, "user not found")
    }
    
    return &pb.GetUserResponse{User: &pb.User{
        Id:    user.ID,
        Name:  user.Name,
        Email: user.Email,
    }}, nil
}
```

## Client Usage

```go
conn, err := grpc.Dial("localhost:50051")
defer conn.Close()

client := pb.NewUserServiceClient(conn)

resp, err := client.GetUser(context.Background(), 
    &pb.GetUserRequest{UserId: "123"})
```

## Streaming

### Server Streaming
```go
func (s *UserServer) ListUsers(req *Empty, 
    stream pb.UserService_ListUsersServer) error {
    
    users := s.repo.GetAll()
    for _, user := range users {
        stream.Send(&pb.User{
            Id:   user.ID,
            Name: user.Name,
        })
    }
    return nil
}
```

### Client Streaming
```go
func (s *UserServer) BulkCreateUsers(
    stream pb.UserService_BulkCreateUsersServer) error {
    
    for {
        req, err := stream.Recv()
        if err == io.EOF {
            return stream.SendAndClose(&pb.Result{Success: true})
        }
        // Process request
    }
}
```

## Error Handling

### Status Codes
- `codes.OK` - Success
- `codes.NotFound` - Resource not found
- `codes.InvalidArgument` - Bad input
- `codes.Internal` - Server error
- `codes.Unavailable` - Service down

### Error Response
```go
return nil, status.Errorf(codes.NotFound, "user %s not found", id)
```

## Interceptors

### Logging
```go
func loggingInterceptor(ctx context.Context, req interface{},
    info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    log.Printf("RPC: %s, Request: %v", info.FullMethod, req)
    resp, err := handler(ctx, req)
    log.Printf("Error: %v", err)
    return resp, err
}

grpc.NewServer(
    grpc.UnaryInterceptor(loggingInterceptor),
)
```

## Testing

```go
func TestGetUser(t *testing.T) {
    server := &UserServer{repo: mockRepo}
    resp, err := server.GetUser(context.Background(), 
        &pb.GetUserRequest{UserId: "123"})
    
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    if resp.User.Name != "John" {
        t.Errorf("expected John, got %s", resp.User.Name)
    }
}
```
