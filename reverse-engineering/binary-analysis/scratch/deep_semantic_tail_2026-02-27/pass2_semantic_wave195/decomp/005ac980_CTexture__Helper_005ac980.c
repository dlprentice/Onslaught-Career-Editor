/* address: 0x005ac980 */
/* name: CTexture__Helper_005ac980 */
/* signature: void __stdcall CTexture__Helper_005ac980(int param_1) */


void CTexture__Helper_005ac980(int param_1)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int unaff_EBX;
  int *piVar7;
  int iVar8;
  undefined4 *puVar9;

  puVar2 = (undefined4 *)(*(code *)**(undefined4 **)(param_1 + 4))(param_1,1,0x74);
  *(undefined4 **)(param_1 + 0x1b0) = puVar2;
  *puVar2 = &LAB_005abae0;
  puVar2[2] = CTexture__Helper_005ac930;
  puVar2[0x1c] = 0;
  if (unaff_EBX != 0) {
    iVar8 = 0;
    if (0 < *(int *)(param_1 + 0x24)) {
      puVar9 = puVar2 + 0x12;
      piVar7 = (int *)(*(int *)(param_1 + 0xdc) + 0xc);
      do {
        iVar3 = *piVar7;
        iVar6 = iVar3;
        if (*(int *)(param_1 + 0xe0) != 0) {
          iVar6 = iVar3 * 3;
        }
        iVar1 = *(int *)(param_1 + 4);
        iVar3 = CDXTexture__AlignUpToMultiple(piVar7[5],iVar3);
        iVar4 = CDXTexture__AlignUpToMultiple(piVar7[4],piVar7[-1]);
        uVar5 = (**(code **)(iVar1 + 0x14))(param_1,1,1,iVar4,iVar3,iVar6);
        *puVar9 = uVar5;
        puVar9 = puVar9 + 1;
        iVar8 = iVar8 + 1;
        piVar7 = piVar7 + 0x15;
      } while (iVar8 < *(int *)(param_1 + 0x24));
    }
    puVar2[1] = &LAB_005abdb0;
    puVar2[3] = &LAB_005abff0;
    puVar2[4] = puVar2 + 0x12;
    return;
  }
  iVar8 = (**(code **)(*(int *)(param_1 + 4) + 4))(param_1,1,0x500);
  puVar2[9] = iVar8 + 0x80;
  puVar2[10] = iVar8 + 0x100;
  puVar2[0xb] = iVar8 + 0x180;
  puVar2[0xc] = iVar8 + 0x200;
  puVar2[0xd] = iVar8 + 0x280;
  puVar2[0xe] = iVar8 + 0x300;
  puVar2[8] = iVar8;
  puVar2[0xf] = iVar8 + 0x380;
  puVar2[0x10] = iVar8 + 0x400;
  puVar2[0x11] = iVar8 + 0x480;
  puVar2[4] = 0;
  puVar2[1] = &LAB_005abda0;
  puVar2[3] = &LAB_005abb00;
  return;
}
