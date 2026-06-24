/* address: 0x005b3080 */
/* name: CDXTexture__InitJpegEncoderWorkingBuffers */
/* signature: void __stdcall CDXTexture__InitJpegEncoderWorkingBuffers(int param_1) */


void CDXTexture__InitJpegEncoderWorkingBuffers(int param_1)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int unaff_EBX;
  int *piVar6;
  int iVar7;
  int iVar8;

  puVar2 = (undefined4 *)(*(code *)**(undefined4 **)(param_1 + 4))(param_1,1,0x68);
  *(undefined4 **)(param_1 + 0x160) = puVar2;
  *puVar2 = &LAB_005b2fc0;
  if (unaff_EBX == 0) {
    iVar8 = (**(code **)(*(int *)(param_1 + 4) + 4))(param_1,1,0x500);
    puVar2[7] = iVar8 + 0x80;
    puVar2[8] = iVar8 + 0x100;
    puVar2[9] = iVar8 + 0x180;
    puVar2[10] = iVar8 + 0x200;
    puVar2[0xb] = iVar8 + 0x280;
    puVar2[0xc] = iVar8 + 0x300;
    puVar2[6] = iVar8;
    puVar2[0xd] = iVar8 + 0x380;
    puVar2[0xe] = iVar8 + 0x400;
    puVar2[0xf] = iVar8 + 0x480;
    puVar2[0x10] = 0;
  }
  else {
    iVar8 = 0;
    if (0 < *(int *)(param_1 + 0x3c)) {
      piVar6 = (int *)(*(int *)(param_1 + 0x44) + 0xc);
      puVar2 = puVar2 + 0x10;
      do {
        iVar7 = *piVar6;
        iVar1 = *(int *)(param_1 + 4);
        iVar3 = CDXTexture__AlignUpToMultiple(piVar6[5],iVar7);
        iVar4 = CDXTexture__AlignUpToMultiple(piVar6[4],piVar6[-1]);
        uVar5 = (**(code **)(iVar1 + 0x14))(param_1,1,0,iVar4,iVar3,iVar7);
        iVar7 = *(int *)(param_1 + 0x3c);
        *puVar2 = uVar5;
        iVar8 = iVar8 + 1;
        puVar2 = puVar2 + 1;
        piVar6 = piVar6 + 0x15;
      } while (iVar8 < iVar7);
      return;
    }
  }
  return;
}
