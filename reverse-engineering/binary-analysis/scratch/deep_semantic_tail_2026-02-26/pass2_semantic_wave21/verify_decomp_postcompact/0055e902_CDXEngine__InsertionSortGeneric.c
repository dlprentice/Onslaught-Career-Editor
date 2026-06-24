/* address: 0x0055e902 */
/* name: CDXEngine__InsertionSortGeneric */
/* signature: void __cdecl CDXEngine__InsertionSortGeneric(uint param_1, uint param_2, int param_3, void * param_4) */


void __cdecl CDXEngine__InsertionSortGeneric(uint param_1,uint param_2,int param_3,void *param_4)

{
  int iVar1;
  void *pvVar2;
  void *pvVar3;

  for (; pvVar2 = (void *)param_1, pvVar3 = (void *)param_1, param_1 < param_2;
      param_2 = param_2 - param_3) {
    while (pvVar3 = (void *)((int)pvVar3 + param_3), pvVar3 <= param_2) {
      iVar1 = (*param_4)(pvVar3,pvVar2);
      if (0 < iVar1) {
        pvVar2 = pvVar3;
      }
    }
    CDXEngine__Helper_0055e950(pvVar2,(void *)param_2,param_3);
  }
  return;
}
