/* address: 0x005b8110 */
/* name: CDXTexture__InitJpegScanController */
/* signature: void __stdcall CDXTexture__InitJpegScanController(int param_1) */


void CDXTexture__InitJpegScanController(int param_1)

{
  int iVar1;
  undefined4 *puVar2;
  int unaff_EBX;

  puVar2 = (undefined4 *)(*(code *)**(undefined4 **)(param_1 + 4))(param_1,1,0x24);
  *(undefined4 **)(param_1 + 0x154) = puVar2;
  *puVar2 = CDXTexture__ProcessJpegScanStateMachine;
  puVar2[1] = CDXTexture__AbortJpegScanStateMachine;
  puVar2[2] = &LAB_005b8090;
  puVar2[4] = 0;
  CTexture__Helper_005b7770();
  if (*(int *)(param_1 + 0xac) == 0) {
    *(undefined4 *)(param_1 + 0xec) = 0;
    *(undefined4 *)(param_1 + 0xa8) = 1;
  }
  else {
    CDXTexture__ValidateJpegScanScript();
  }
  if (*(int *)(param_1 + 0xec) != 0) {
    *(undefined4 *)(param_1 + 0xb8) = 1;
  }
  if (unaff_EBX == 0) {
    puVar2[5] = 0;
  }
  else {
    puVar2[5] = (*(int *)(param_1 + 0xb8) == 0) + 1;
  }
  iVar1 = *(int *)(param_1 + 0xb8);
  puVar2[8] = 0;
  puVar2[6] = 0;
  if (iVar1 != 0) {
    puVar2[7] = *(int *)(param_1 + 0xa8) << 1;
    return;
  }
  puVar2[7] = *(undefined4 *)(param_1 + 0xa8);
  return;
}
