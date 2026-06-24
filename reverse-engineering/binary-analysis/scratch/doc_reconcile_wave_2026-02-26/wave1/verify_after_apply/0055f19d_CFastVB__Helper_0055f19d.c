/* address: 0x0055f19d */
/* name: CFastVB__Helper_0055f19d */
/* signature: uint __cdecl CFastVB__Helper_0055f19d(void * param_1, uint param_2, uint param_3, void * param_4) */


uint __cdecl CFastVB__Helper_0055f19d(void *param_1,uint param_2,uint param_3,void *param_4)

{
  void *pvVar1;
  int iVar2;
  void *pvVar3;
  uint uVar4;
  void *pvVar5;
  void *pvVar6;
  void *pvVar7;

  pvVar1 = param_4;
  pvVar6 = (void *)(param_2 * param_3);
  if (pvVar6 == (void *)0x0) {
    param_3 = 0;
  }
  else {
    pvVar5 = pvVar6;
    if ((*(ushort *)((int)param_4 + 0xc) & 0x10c) == 0) {
      param_4 = (void *)0x1000;
    }
    else {
      param_4 = *(void **)((int)param_4 + 0x18);
    }
    do {
      uVar4 = *(uint *)((int)pvVar1 + 0xc) & 0x108;
      if ((uVar4 == 0) || (pvVar7 = *(void **)((int)pvVar1 + 4), pvVar7 == (void *)0x0)) {
        if (param_4 <= pvVar5) {
          if ((uVar4 != 0) && (iVar2 = CDXTexture__Helper_00564f7a(pvVar1), iVar2 != 0)) {
LAB_0055f29e:
            return (uint)((int)pvVar6 - (int)pvVar5) / param_2;
          }
          pvVar7 = pvVar5;
          if (param_4 != (void *)0x0) {
            pvVar7 = (void *)((int)pvVar5 - (uint)pvVar5 % (uint)param_4);
          }
          pvVar3 = (void *)CTexture__Helper_00567505
                                     (*(uint *)((int)pvVar1 + 0x10),(int)param_1,(int)pvVar7);
          if ((pvVar3 == (void *)0xffffffff) ||
             (pvVar5 = (void *)((int)pvVar5 - (int)pvVar3), pvVar3 < pvVar7)) {
            *(uint *)((int)pvVar1 + 0xc) = *(uint *)((int)pvVar1 + 0xc) | 0x20;
            goto LAB_0055f29e;
          }
          goto LAB_0055f255;
        }
        uVar4 = CDXTexture__Helper_0056171c((int)*(char *)param_1,pvVar1);
        if (uVar4 == 0xffffffff) goto LAB_0055f29e;
        param_1 = (void *)((int)param_1 + 1);
        param_4 = *(void **)((int)pvVar1 + 0x18);
        pvVar5 = (void *)((int)pvVar5 - 1);
        if ((int)param_4 < 1) {
          param_4 = (void *)0x1;
        }
      }
      else {
        pvVar3 = pvVar5;
        if (pvVar7 <= pvVar5) {
          pvVar3 = pvVar7;
        }
        CTexture__Helper_00567700(*(void **)pvVar1,param_1,(uint)pvVar3);
        *(int *)((int)pvVar1 + 4) = *(int *)((int)pvVar1 + 4) - (int)pvVar3;
        *(int *)pvVar1 = *(int *)pvVar1 + (int)pvVar3;
        pvVar5 = (void *)((int)pvVar5 - (int)pvVar3);
LAB_0055f255:
        param_1 = (void *)((int)param_1 + (int)pvVar3);
      }
    } while (pvVar5 != (void *)0x0);
  }
  return param_3;
}
