/* address: 0x0057db30 */
/* name: CFastVB__Helper_0057db30 */
/* signature: int __fastcall CFastVB__Helper_0057db30(void * param_1) */


int __fastcall CFastVB__Helper_0057db30(void *param_1)

{
  byte *pbVar1;
  int iVar2;
  byte *pbVar3;
  undefined1 *puVar4;
  byte *pbVar5;
  byte *pbVar6;
  int iVar7;
  undefined1 *local_c;

  puVar4 = *(undefined1 **)(*(int *)((int)param_1 + 4) + 0x20);
  iVar2 = *(int *)param_1;
  pbVar3 = *(byte **)(iVar2 + 0x20);
  iVar7 = *(int *)(iVar2 + 0x1058);
  pbVar5 = pbVar3 + *(int *)(iVar2 + 0x1064) * iVar7;
  for (; pbVar3 < pbVar5; pbVar3 = pbVar3 + iVar7 * 2) {
    iVar2 = *(int *)(iVar2 + 0x1060);
    pbVar6 = pbVar3 + iVar7;
    local_c = puVar4;
    for (pbVar1 = pbVar3; pbVar1 < pbVar3 + iVar2; pbVar1 = pbVar1 + 2) {
      *local_c = (char)((uint)pbVar6[1] + (uint)pbVar1[1] + (uint)*pbVar6 + 2 + (uint)*pbVar1 >> 2);
      pbVar6 = pbVar6 + 2;
      local_c = local_c + 1;
    }
    puVar4 = puVar4 + *(int *)(*(int *)((int)param_1 + 4) + 0x1058);
    iVar2 = *(int *)param_1;
    iVar7 = *(int *)(iVar2 + 0x1058);
  }
  return 0;
}
