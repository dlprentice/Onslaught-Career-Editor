/* address: 0x00572310 */
/* name: CDXTexture__InsertUniqueTripletAtFront */
/* signature: void __stdcall CDXTexture__InsertUniqueTripletAtFront(void * param_1, void * param_2) */


void CDXTexture__InsertUniqueTripletAtFront(void *param_1,void *param_2)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int *piVar4;

  iVar2 = *(int *)((int)param_1 + 4);
  iVar3 = 0;
  if (0 < iVar2) {
    piVar4 = *(int **)param_1;
    do {
      if (*piVar4 == *(int *)param_2) goto LAB_0057234e;
      iVar3 = iVar3 + 1;
      piVar4 = piVar4 + 1;
    } while (iVar3 < iVar2);
  }
  uVar1 = *(undefined4 *)param_2;
  iVar2 = iVar2 + -2;
  while (-1 < iVar2) {
    iVar2 = iVar2 + -1;
    *(undefined4 *)(*(int *)param_1 + 8 + iVar2 * 4) =
         *(undefined4 *)(*(int *)param_1 + 4 + iVar2 * 4);
  }
  **(undefined4 **)param_1 = uVar1;
LAB_0057234e:
  iVar2 = *(int *)((int)param_1 + 4);
  iVar3 = 0;
  if (0 < iVar2) {
    piVar4 = *(int **)param_1;
    do {
      if (*piVar4 == *(int *)((int)param_2 + 4)) goto LAB_00572383;
      iVar3 = iVar3 + 1;
      piVar4 = piVar4 + 1;
    } while (iVar3 < iVar2);
  }
  uVar1 = *(undefined4 *)((int)param_2 + 4);
  iVar2 = iVar2 + -2;
  while (-1 < iVar2) {
    iVar2 = iVar2 + -1;
    *(undefined4 *)(*(int *)param_1 + 8 + iVar2 * 4) =
         *(undefined4 *)(*(int *)param_1 + 4 + iVar2 * 4);
  }
  **(undefined4 **)param_1 = uVar1;
LAB_00572383:
  iVar2 = *(int *)((int)param_1 + 4);
  iVar3 = 0;
  if (0 < iVar2) {
    piVar4 = *(int **)param_1;
    do {
      if (*piVar4 == *(int *)((int)param_2 + 8)) {
        return;
      }
      iVar3 = iVar3 + 1;
      piVar4 = piVar4 + 1;
    } while (iVar3 < iVar2);
  }
  uVar1 = *(undefined4 *)((int)param_2 + 8);
  iVar2 = iVar2 + -2;
  while (-1 < iVar2) {
    iVar2 = iVar2 + -1;
    *(undefined4 *)(*(int *)param_1 + 8 + iVar2 * 4) =
         *(undefined4 *)(*(int *)param_1 + 4 + iVar2 * 4);
  }
  **(undefined4 **)param_1 = uVar1;
  return;
}
