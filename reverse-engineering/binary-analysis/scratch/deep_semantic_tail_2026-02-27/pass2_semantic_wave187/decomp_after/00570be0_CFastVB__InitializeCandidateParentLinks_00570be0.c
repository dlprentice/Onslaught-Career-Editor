/* address: 0x00570be0 */
/* name: CFastVB__InitializeCandidateParentLinks_00570be0 */
/* signature: void __stdcall CFastVB__InitializeCandidateParentLinks_00570be0(int param_1, int param_2) */


void CFastVB__InitializeCandidateParentLinks_00570be0(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  void *unaff_EDI;
  int iVar5;
  int local_8;
  int local_4;

  iVar4 = 0;
  if (*(int *)(param_2 + 4) == 0) {
    local_8 = 0;
  }
  else {
    local_8 = *(int *)(param_2 + 8) - *(int *)(param_2 + 4) >> 2;
  }
  if (0 < local_8) {
    do {
      local_4 = *(int *)(*(int *)(param_2 + 4) + iVar4 * 4);
      *(undefined4 *)(local_4 + 0x20) = 0xffffffff;
      CFastVB__InsertDwordSpanFilled
                ((void *)param_1,*(int *)(param_1 + 8),(void *)0x1,(uint)&local_4,unaff_EDI);
      iVar1 = *(int *)(*(int *)(param_2 + 4) + iVar4 * 4);
      if (*(int *)(iVar1 + 0x10) == 0) {
        iVar3 = 0;
      }
      else {
        iVar3 = *(int *)(iVar1 + 0x14) - *(int *)(iVar1 + 0x10) >> 2;
      }
      iVar5 = 0;
      if (0 < iVar3) {
        do {
          iVar2 = *(int *)(*(int *)(iVar1 + 0x10) + iVar5 * 4);
          if (*(int *)(local_4 + 0x20) < 0) {
            *(undefined4 *)(iVar2 + 0x14) = 0xffffffff;
            *(undefined4 *)(iVar2 + 0xc) = *(undefined4 *)(local_4 + 0x1c);
          }
          else {
            *(int *)(iVar2 + 0x14) = *(int *)(local_4 + 0x20);
            *(undefined4 *)(iVar2 + 0x10) = *(undefined4 *)(local_4 + 0x1c);
          }
          iVar5 = iVar5 + 1;
        } while (iVar5 < iVar3);
      }
      iVar4 = iVar4 + 1;
    } while (iVar4 < local_8);
  }
  return;
}
