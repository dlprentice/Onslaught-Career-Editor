/* address: 0x0056fec0 */
/* name: CFastVB__Helper_0056fec0 */
/* signature: void __cdecl CFastVB__Helper_0056fec0(void * param_1, void * param_2, void * param_3, void * param_4) */


void __cdecl CFastVB__Helper_0056fec0(void *param_1,void *param_2,void *param_3,void *param_4)

{
  int iVar1;

  *(undefined4 *)param_3 = 0xffffffff;
  *(undefined4 *)param_4 = 0xffffffff;
  iVar1 = *(int *)param_2;
  if (((iVar1 == *(int *)param_1) || (iVar1 == *(int *)((int)param_1 + 4))) ||
     (iVar1 == *(int *)((int)param_1 + 8))) {
    if (*(int *)param_3 != -1) goto LAB_0056ff2e;
    *(int *)param_3 = iVar1;
  }
  iVar1 = *(int *)((int)param_2 + 4);
  if (((iVar1 == *(int *)param_1) || (iVar1 == *(int *)((int)param_1 + 4))) ||
     (iVar1 == *(int *)((int)param_1 + 8))) {
    if (*(int *)param_3 != -1) goto LAB_0056ff2e;
    *(int *)param_3 = iVar1;
  }
  iVar1 = *(int *)((int)param_2 + 8);
  if (((iVar1 != *(int *)param_1) && (iVar1 != *(int *)((int)param_1 + 4))) &&
     (iVar1 != *(int *)((int)param_1 + 8))) {
    return;
  }
  if (*(int *)param_3 == -1) {
    *(int *)param_3 = iVar1;
    return;
  }
LAB_0056ff2e:
  *(int *)param_4 = iVar1;
  return;
}
