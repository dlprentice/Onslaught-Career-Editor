/* address: 0x005b3e80 */
/* name: CDXTexture__InitJpegEntropyEncoderState */
/* signature: void __stdcall CDXTexture__InitJpegEntropyEncoderState(int param_1) */


void CDXTexture__InitJpegEntropyEncoderState(int param_1)

{
  undefined4 *puVar1;
  int iVar2;

  puVar1 = (undefined4 *)(*(code *)**(undefined4 **)(param_1 + 4))(param_1,1,0x6c);
  *(undefined4 **)(param_1 + 0x174) = puVar1;
  *puVar1 = &LAB_005b3d20;
  puVar1 = puVar1 + 0xb;
  iVar2 = 4;
  do {
    puVar1[4] = 0;
    *puVar1 = 0;
    puVar1[0xc] = 0;
    puVar1[8] = 0;
    puVar1 = puVar1 + 1;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return;
}
