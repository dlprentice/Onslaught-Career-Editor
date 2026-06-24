/* address: 0x0056eab4 */
/* name: CRT__CloneEnvironmentTable */
/* signature: int __cdecl CRT__CloneEnvironmentTable(void * param_1) */


int __cdecl CRT__CloneEnvironmentTable(void *param_1)

{
  int iVar1;
  int *piVar2;
  undefined4 *puVar3;
  void *pvVar4;
  uint *puVar5;
  int iVar6;
  undefined4 *puVar7;

  iVar6 = 0;
  if (param_1 != (void *)0x0) {
    iVar1 = *(int *)param_1;
    piVar2 = param_1;
    while (iVar1 != 0) {
      piVar2 = piVar2 + 1;
      iVar6 = iVar6 + 1;
      iVar1 = *piVar2;
    }
    puVar3 = _malloc(iVar6 * 4 + 4);
    if (puVar3 == (undefined4 *)0x0) {
      __amsg_exit(9);
    }
    pvVar4 = *(void **)param_1;
    puVar7 = puVar3;
    while (pvVar4 != (void *)0x0) {
      param_1 = (void *)((int)param_1 + 4);
      puVar5 = CRT__StrDup(pvVar4);
      *puVar7 = puVar5;
      puVar7 = puVar7 + 1;
      pvVar4 = *(void **)param_1;
    }
    *puVar7 = 0;
    return (int)puVar3;
  }
  return 0;
}
