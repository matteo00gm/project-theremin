package action

import (
	"log"

	"github.com/go-vgo/robotgo"
)

// MouseController manages operating system cursor interactions.
type MouseController struct {
	ScreenWidth  int
	ScreenHeight int
}

// NewMouseController initializes the controller with the primary display dimensions.
func NewMouseController() *MouseController {
	width, height := robotgo.GetScreenSize()
	log.Printf("Screen dimensions detected: %dx%d", width, height)

	return &MouseController{
		ScreenWidth:  width,
		ScreenHeight: height,
	}
}

// MoveCursor translates normalized coordinates (0.0 to 1.0) into absolute screen pixels.
func (m *MouseController) MoveCursor(x, y float32) {
	pixelX := int(x * float32(m.ScreenWidth))
	pixelY := int(y * float32(m.ScreenHeight))

	robotgo.Move(pixelX, pixelY)
}
