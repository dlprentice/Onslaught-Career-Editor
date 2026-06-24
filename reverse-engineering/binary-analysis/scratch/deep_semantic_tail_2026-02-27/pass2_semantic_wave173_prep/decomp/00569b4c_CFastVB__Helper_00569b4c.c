/* address: 0x00569b4c */
/* name: CFastVB__Helper_00569b4c */
/* signature: int * __cdecl CFastVB__Helper_00569b4c(int param_1, int param_2, void * param_3, void * param_4) */


int * __cdecl CFastVB__Helper_00569b4c(int param_1,int param_2,void *param_3,void *param_4)

{
  void *pvVar1;
  void *pvVar2;
  int iVar3;
  short local_2c;
  char local_2a;
  undefined1 local_28 [24];
  undefined1 local_10 [12];

  CFastVB__Helper_00569ba8(local_10,&param_1);
  iVar3 = CTexture__Helper_0056d647();
  pvVar2 = param_4;
  pvVar1 = param_3;
  *(int *)((int)param_3 + 8) = iVar3;
  *(int *)param_3 = (int)local_2a;
  *(int *)((int)param_3 + 4) = (int)local_2c;
  CRT__StrCpyAligned(param_4,local_28);
  *(void **)((int)pvVar1 + 0xc) = pvVar2;
  return pvVar1;
}
