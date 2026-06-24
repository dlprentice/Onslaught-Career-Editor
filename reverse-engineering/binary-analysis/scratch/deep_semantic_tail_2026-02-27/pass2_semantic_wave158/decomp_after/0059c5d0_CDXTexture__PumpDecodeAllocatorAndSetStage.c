/* address: 0x0059c5d0 */
/* name: CDXTexture__PumpDecodeAllocatorAndSetStage */
/* signature: void __stdcall CDXTexture__PumpDecodeAllocatorAndSetStage(int param_1) */


void CDXTexture__PumpDecodeAllocatorAndSetStage(int param_1)

{
  if (*(int *)(param_1 + 4) != 0) {
    (**(code **)(*(int *)(param_1 + 4) + 0x24))(param_1,1);
    if (*(int *)(param_1 + 0x10) != 0) {
      *(undefined4 *)(param_1 + 0x14) = 200;
      *(undefined4 *)(param_1 + 0x134) = 0;
      return;
    }
    *(undefined4 *)(param_1 + 0x14) = 100;
  }
  return;
}
