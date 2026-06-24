# CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture

- Address: 0x00469390
- Status: Renamed (headless batch, Wave 377 read-back verified)
- Current saved signature: `uint __cdecl CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture(float x, float y, float width, float height, int dispatch_context)`

## Purpose

Processes the modal mouse-input readiness gate and otherwise dispatches a rectangle interaction through the VBufTexture/click path.

## Notes

Wave 377 hardened the saved signature/comment/tag. Static decompile/xref evidence shows four float rectangle arguments plus a dispatch context routed into the frontend rectangle input dispatcher when modal mouse input does not consume the event.

This is static evidence only. Runtime mouse behavior remains unproven by this page.
