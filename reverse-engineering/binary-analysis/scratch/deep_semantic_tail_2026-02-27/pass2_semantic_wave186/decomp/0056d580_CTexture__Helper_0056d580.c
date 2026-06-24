/* address: 0x0056d580 */
/* name: CTexture__Helper_0056d580 */
/* signature: void __cdecl CTexture__Helper_0056d580(void * param_1, int param_2, void * param_3) */


void __cdecl CTexture__Helper_0056d580(void *param_1,int param_2,void *param_3)

{
  void *pvVar1;
  int local_14;
  undefined4 local_10;
  undefined4 local_c;
  int local_8;

  pvVar1 = param_3;
  local_8 = 0x404e;
  *(undefined4 *)param_3 = 0;
  *(undefined4 *)((int)param_3 + 4) = 0;
  *(undefined4 *)((int)param_3 + 8) = 0;
  if (param_2 != 0) {
    param_3 = (void *)param_2;
    do {
      local_14 = *(int *)pvVar1;
      local_10 = *(undefined4 *)((int)pvVar1 + 4);
      local_c = *(undefined4 *)((int)pvVar1 + 8);
      CTexture__Helper_0056d525(pvVar1);
      CTexture__Helper_0056d525(pvVar1);
      ___add_12(pvVar1,&local_14);
      CTexture__Helper_0056d525(pvVar1);
      local_10 = 0;
      local_c = 0;
      local_14 = (int)*(char *)param_1;
      ___add_12(pvVar1,&local_14);
      param_1 = (void *)((int)param_1 + 1);
      param_3 = (void *)((int)param_3 + -1);
    } while (param_3 != (void *)0x0);
  }
  while (*(int *)((int)pvVar1 + 8) == 0) {
    *(uint *)((int)pvVar1 + 8) = *(uint *)((int)pvVar1 + 4) >> 0x10;
    local_8 = local_8 + 0xfff0;
    *(uint *)((int)pvVar1 + 4) = *(uint *)pvVar1 >> 0x10 | *(uint *)((int)pvVar1 + 4) << 0x10;
    *(uint *)pvVar1 = *(uint *)pvVar1 << 0x10;
  }
  while ((*(uint *)((int)pvVar1 + 8) & 0x8000) == 0) {
    CTexture__Helper_0056d525(pvVar1);
    local_8 = local_8 + 0xffff;
  }
  *(undefined2 *)((int)pvVar1 + 10) = (undefined2)local_8;
  return;
}
