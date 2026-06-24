/* address: 0x004bed30 */
/* name: CExplosionInitThing__StepToLowestCostNeighbor8 */
/* signature: void __cdecl CExplosionInitThing__StepToLowestCostNeighbor8(void * param_1, void * param_2) */


void __cdecl CExplosionInitThing__StepToLowestCostNeighbor8(void *param_1,void *param_2)

{
  int iVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  ushort uVar5;
  int iVar6;
  int iVar7;

  iVar3 = *(int *)param_1;
  iVar4 = *(int *)param_2;
  iVar1 = iVar3 * 0x100 + iVar4;
  uVar5 = *(ushort *)((int)&DAT_00809dc0 + iVar1 * 2);
  iVar6 = iVar3;
  if ((0 < iVar3) && (*(ushort *)(&DAT_00809bc0 + iVar1 * 2) < uVar5)) {
    iVar6 = iVar3 + -1;
    uVar5 = *(ushort *)(&DAT_00809bc0 + iVar1 * 2);
  }
  if ((iVar3 < 0xff) && (uVar2 = *(ushort *)((int)&DAT_00809fc0 + iVar1 * 2), uVar2 < uVar5)) {
    iVar6 = iVar3 + 1;
    uVar5 = uVar2;
  }
  iVar7 = iVar4;
  if ((0 < iVar4) && (uVar2 = *(ushort *)((int)&DAT_00809dbc + iVar1 * 2 + 2), uVar2 < uVar5)) {
    iVar7 = iVar4 + -1;
    iVar6 = iVar3;
    uVar5 = uVar2;
  }
  if ((iVar4 < 0xff) && (uVar2 = *(ushort *)((int)&DAT_00809dc0 + iVar1 * 2 + 2), uVar2 < uVar5)) {
    iVar7 = iVar4 + 1;
    iVar6 = iVar3;
    uVar5 = uVar2;
  }
  if (((0 < iVar3) && (0 < iVar4)) && (*(ushort *)(&DAT_00809bbe + iVar1 * 2) < uVar5)) {
    iVar6 = iVar3 + -1;
    iVar7 = iVar4 + -1;
    uVar5 = *(ushort *)(&DAT_00809bbe + iVar1 * 2);
  }
  if (((iVar3 < 0xff) && (0 < iVar4)) && (*(ushort *)(&DAT_00809fbe + iVar1 * 2) < uVar5)) {
    iVar6 = iVar3 + 1;
    iVar7 = iVar4 + -1;
    uVar5 = *(ushort *)(&DAT_00809fbe + iVar1 * 2);
  }
  if (((0 < iVar3) && (iVar4 < 0xff)) && (*(ushort *)(&DAT_00809bc2 + iVar1 * 2) < uVar5)) {
    iVar6 = iVar3 + -1;
    iVar7 = iVar4 + 1;
    uVar5 = *(ushort *)(&DAT_00809bc2 + iVar1 * 2);
  }
  if (0xfe < iVar3) {
    *(int *)param_1 = iVar6;
    *(int *)param_2 = iVar7;
    return;
  }
  if (0xfe < iVar4) {
    *(int *)param_1 = iVar6;
    *(int *)param_2 = iVar7;
    return;
  }
  if (uVar5 <= *(ushort *)((int)&DAT_00809fc0 + iVar1 * 2 + 2)) {
    *(int *)param_1 = iVar6;
    *(int *)param_2 = iVar7;
    return;
  }
  *(int *)param_1 = iVar3 + 1;
  *(int *)param_2 = iVar4 + 1;
  return;
}
