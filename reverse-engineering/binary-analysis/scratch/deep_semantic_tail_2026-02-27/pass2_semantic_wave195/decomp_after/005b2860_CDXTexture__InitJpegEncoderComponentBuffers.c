/* address: 0x005b2860 */
/* name: CDXTexture__InitJpegEncoderComponentBuffers */
/* signature: void __stdcall CDXTexture__InitJpegEncoderComponentBuffers(void * param_1) */


void CDXTexture__InitJpegEncoderComponentBuffers(void *param_1)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  int unaff_ESI;
  int *piVar4;

  puVar1 = (undefined4 *)(*(code *)**(undefined4 **)((int)param_1 + 4))(param_1,1,0x40);
  iVar3 = *(int *)((int)param_1 + 0xb0);
  *(undefined4 **)((int)param_1 + 0x158) = puVar1;
  *puVar1 = &LAB_005b2810;
  if (iVar3 == 0) {
    if (unaff_ESI != 0) {
      puVar1 = *(undefined4 **)param_1;
      puVar1[5] = 4;
      (*(code *)*puVar1)(param_1);
      return;
    }
    iVar3 = 0;
    if (0 < *(int *)((int)param_1 + 0x3c)) {
      piVar4 = (int *)(*(int *)((int)param_1 + 0x44) + 0x1c);
      puVar1 = puVar1 + 6;
      do {
        uVar2 = (**(code **)(*(int *)((int)param_1 + 4) + 8))
                          (param_1,1,*piVar4 << 3,piVar4[-4] << 3);
        *puVar1 = uVar2;
        iVar3 = iVar3 + 1;
        puVar1 = puVar1 + 1;
        piVar4 = piVar4 + 0x15;
      } while (iVar3 < *(int *)((int)param_1 + 0x3c));
    }
  }
  return;
}
