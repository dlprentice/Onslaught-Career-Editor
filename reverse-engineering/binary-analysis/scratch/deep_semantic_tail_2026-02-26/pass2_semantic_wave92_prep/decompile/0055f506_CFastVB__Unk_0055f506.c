/* address: 0x0055f506 */
/* name: CFastVB__Unk_0055f506 */
/* signature: uint __cdecl CFastVB__Unk_0055f506(void * param_1, uint param_2, uint param_3, void * param_4) */


uint __cdecl CFastVB__Unk_0055f506(void *param_1,uint param_2,uint param_3,void *param_4)

{
  void *pvVar1;
  void *pvVar2;
  int iVar3;
  uint uVar4;
  undefined1 *puVar5;
  void *pvVar6;
  void *pvVar7;

  pvVar1 = param_4;
  pvVar6 = (void *)(param_2 * param_3);
  if (pvVar6 == (void *)0x0) {
    param_3 = 0;
  }
  else {
    puVar5 = param_1;
    param_1 = pvVar6;
    if ((*(ushort *)((int)param_4 + 0xc) & 0x10c) == 0) {
      param_4 = (void *)0x1000;
    }
    else {
      param_4 = *(void **)((int)param_4 + 0x18);
    }
    do {
      if (((*(ushort *)((int)pvVar1 + 0xc) & 0x10c) == 0) ||
         (pvVar2 = *(void **)((int)pvVar1 + 4), pvVar2 == (void *)0x0)) {
        if (param_1 < param_4) {
          uVar4 = CFastVB__Helper_00567aba(pvVar1);
          if (uVar4 == 0xffffffff) goto LAB_0055f5e2;
          *puVar5 = (char)uVar4;
          param_4 = *(void **)((int)pvVar1 + 0x18);
          puVar5 = puVar5 + 1;
          param_1 = (void *)((int)param_1 + -1);
        }
        else {
          pvVar2 = param_1;
          if (param_4 != (void *)0x0) {
            pvVar2 = (void *)((int)param_1 - (uint)param_1 % (uint)param_4);
          }
          iVar3 = CFastVB__Helper_00567b96(*(uint *)((int)pvVar1 + 0x10),(int)puVar5,(int)pvVar2);
          if (iVar3 == 0) {
            *(uint *)((int)pvVar1 + 0xc) = *(uint *)((int)pvVar1 + 0xc) | 0x10;
LAB_0055f5e2:
            return (uint)((int)pvVar6 - (int)param_1) / param_2;
          }
          if (iVar3 == -1) {
            *(uint *)((int)pvVar1 + 0xc) = *(uint *)((int)pvVar1 + 0xc) | 0x20;
            goto LAB_0055f5e2;
          }
          param_1 = (void *)((int)param_1 - iVar3);
          puVar5 = puVar5 + iVar3;
        }
      }
      else {
        pvVar7 = param_1;
        if (pvVar2 <= param_1) {
          pvVar7 = pvVar2;
        }
        CTexture__Helper_00567700(puVar5,*(void **)pvVar1,(uint)pvVar7);
        param_1 = (void *)((int)param_1 - (int)pvVar7);
        *(int *)((int)pvVar1 + 4) = *(int *)((int)pvVar1 + 4) - (int)pvVar7;
        *(int *)pvVar1 = *(int *)pvVar1 + (int)pvVar7;
        puVar5 = puVar5 + (int)pvVar7;
      }
    } while (param_1 != (void *)0x0);
  }
  return param_3;
}
