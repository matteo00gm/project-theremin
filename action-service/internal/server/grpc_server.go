package server

import (
	"fmt"
	"io"
	"log"
	"time"

	pb "action-service/pb"
)

type GazeServer struct {
	pb.UnimplementedEyeTrackerServer
}

func NewGazeServer() *GazeServer {
	return &GazeServer{}
}

// StreamCoordinates is the function the vision service calls to start streaming data
func (s *GazeServer) StreamCoordinates(stream pb.EyeTracker_StreamCoordinatesServer) error {
	log.Println("Vision Sensor connected to the stream!")

	for {
		point, err := stream.Recv()

		if err == io.EOF {
			log.Println("Vision Sensor disconnected cleanly.")
			return stream.SendAndClose(&pb.StreamStatus{
				Success: true,
				Message: "Stream ended normally",
			})
		}

		if err != nil {
			log.Printf("Error receiving from stream: %v", err)
			return err
		}

		// Calculate latency
		now := time.Now().UnixMilli()
		latency := now - point.Timestamp

		fmt.Printf("Received -> X: %.4f, Y: %.4f | Conf: %.2f | Latency: %dms\n",
			point.X, point.Y, point.Confidence, latency)

	}
}
