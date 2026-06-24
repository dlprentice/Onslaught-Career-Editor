/* address: 0x005af860 */
/* name: CDXTexture__BuildYccToRgbLookupTables */
/* signature: void CDXTexture__BuildYccToRgbLookupTables(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__BuildYccToRgbLookupTables(void)

{
  undefined4 *puVar1;
  int in_EAX;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  undefined1 *puVar8;
  int iVar9;
  int iVar10;

  iVar4 = *(int *)(in_EAX + 0x1cc);
  uVar2 = (*(code *)**(undefined4 **)(in_EAX + 4))();
  puVar1 = *(undefined4 **)(in_EAX + 4);
  *(undefined4 *)(iVar4 + 8) = uVar2;
  uVar2 = (*(code *)*puVar1)();
  puVar1 = *(undefined4 **)(in_EAX + 4);
  *(undefined4 *)(iVar4 + 0xc) = uVar2;
  uVar2 = (*(code *)*puVar1)();
  *(undefined4 *)(iVar4 + 0x10) = uVar2;
  iVar3 = (*(code *)**(undefined4 **)(in_EAX + 4))();
  piVar5 = *(int **)(iVar4 + 0xc);
  *(int *)(iVar4 + 0x14) = iVar3;
  iVar10 = *(int *)(iVar4 + 0x10) - (int)piVar5;
  iVar4 = *(int *)(iVar4 + 8) - (int)piVar5;
  iVar3 = iVar3 - (int)piVar5;
  puVar8 = &LAB_005b6900;
  iVar7 = -0xe25100;
  iVar9 = -0xb2f480;
  iVar6 = 0x2c8d00;
  do {
    *(int *)(iVar4 + (int)piVar5) = iVar9 >> 0x10;
    *piVar5 = iVar7 >> 0x10;
    *(undefined1 **)(iVar10 + (int)piVar5) = puVar8;
    *(int *)(iVar3 + (int)piVar5) = iVar6;
    iVar6 = iVar6 + -0x581a;
    iVar9 = iVar9 + 0x166e9;
    iVar7 = iVar7 + 0x1c5a2;
    puVar8 = puVar8 + -0xb6d2;
    piVar5 = piVar5 + 1;
  } while (-0x2b34e7 < iVar6);
  return;
}
