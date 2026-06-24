/* address: 0x0057dbcb */
/* name: CFastVB__Helper_0057dbcb */
/* signature: int __fastcall CFastVB__Helper_0057dbcb(void * param_1) */


int __fastcall CFastVB__Helper_0057dbcb(void *param_1)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  int iVar5;
  ushort *puVar6;
  int iVar7;
  ushort *puVar8;
  ushort *puVar9;
  ushort *puVar10;
  ushort *puVar11;
  ushort *puVar12;

  iVar5 = *(int *)param_1;
  puVar6 = *(ushort **)(*(int *)((int)param_1 + 4) + 0x20);
  iVar7 = *(int *)(iVar5 + 0x1058);
  puVar8 = *(ushort **)(iVar5 + 0x20);
  puVar12 = (ushort *)(*(int *)(iVar5 + 0x1064) * iVar7 + (int)puVar8);
  for (; puVar8 < puVar12; puVar8 = puVar8 + iVar7) {
    iVar5 = *(int *)(iVar5 + 0x1060);
    puVar11 = (ushort *)(iVar7 + (int)puVar8);
    puVar9 = puVar6;
    for (puVar10 = puVar8; puVar10 < puVar8 + iVar5; puVar10 = puVar10 + 2) {
      uVar1 = *puVar10;
      uVar2 = puVar10[1];
      uVar3 = puVar11[1];
      uVar4 = *puVar11;
      puVar11 = puVar11 + 2;
      *puVar9 = (byte)((byte)((uint)(uVar3 & 0xe3) + (uint)(uVar1 & 0xe3) + (uint)(uVar4 & 0xe3) +
                              0x42 + (uint)(uVar2 & 0xe3) >> 2) ^
                      (byte)((uint)(uVar3 & 0xff1c) + (uVar1 & 0xffffff1c) + (uint)(uVar4 & 0xff1c)
                             + 0x208 + (uint)(uVar2 & 0xff1c) >> 2)) & 0xe3 ^
                (ushort)((uVar3 & 0xff1c) + (uVar1 & 0xff1c) + (uVar4 & 0xff1c) + 0x208 +
                         (uVar2 & 0xff1c) >> 2);
      puVar9 = puVar9 + 1;
    }
    puVar6 = (ushort *)((int)puVar6 + *(int *)(*(int *)((int)param_1 + 4) + 0x1058));
    iVar5 = *(int *)param_1;
    iVar7 = *(int *)(iVar5 + 0x1058);
  }
  return 0;
}
