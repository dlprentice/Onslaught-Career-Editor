/* address: 0x005627ea */
/* name: CDXTexture__Helper_005627ea */
/* signature: bool __cdecl CDXTexture__Helper_005627ea(uint param_1, void * param_2, uint param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

bool __cdecl CDXTexture__Helper_005627ea(uint param_1,void *param_2,uint param_3)

{
  bool bVar1;
  uint uVar2;
  bool bVar3;
  double dVar4;
  undefined8 local_10;
  int local_8;

  uVar2 = param_1 & 0x1f;
  bVar1 = true;
  if (((param_1 & 8) != 0) && ((param_3 & 1) != 0)) {
    CDXTexture__Helper_00562c99();
    uVar2 = param_1 & 0x17;
    goto LAB_005629df;
  }
  if (((param_1 & 4) != 0) && ((param_3 & 4) != 0)) {
    CDXTexture__Helper_00562c99();
    uVar2 = param_1 & 0x1b;
    goto LAB_005629df;
  }
  if (((param_1 & 1) == 0) || ((param_3 & 8) == 0)) {
    if (((param_1 & 2) != 0) && ((param_3 & 0x10) != 0)) {
      bVar3 = (param_1 & 0x10) != 0;
      dVar4 = *(double *)param_2;
      if (dVar4 != _DAT_005d87b0) {
        dVar4 = CTexture__Helper_00562b98(SUB84(dVar4,0),(uint)((ulonglong)dVar4 >> 0x20),&local_8);
        local_8 = local_8 + -0x600;
        if (local_8 < -0x432) {
          local_10 = 0.0;
          bVar3 = bVar1;
        }
        else {
          local_10 = (double)(ulonglong)(SUB87(dVar4,0) & 0xfffffffffffff | 0x10000000000000);
          if (local_8 < -0x3fd) {
            local_8 = -0x3fd - local_8;
            do {
              if ((((ulonglong)local_10 & 1) != 0) && (!bVar3)) {
                bVar3 = bVar1;
              }
              uVar2 = (uint)local_10 >> 1;
              if (((ulonglong)local_10 & 0x100000000) != 0) {
                local_10._3_1_ = (byte)((ulonglong)local_10 >> 0x18) >> 1;
                local_10._0_3_ = (undefined3)uVar2;
                local_10._0_4_ = CONCAT13(local_10._3_1_,(undefined3)local_10) | 0x80000000;
                uVar2 = (uint)local_10;
              }
              local_10._0_4_ = uVar2;
              local_10 = (double)CONCAT44(local_10._4_4_ >> 1,(uint)local_10);
              local_8 = local_8 + -1;
            } while (local_8 != 0);
          }
          if (dVar4 < _DAT_005d87b0) {
            local_10 = -local_10;
          }
        }
        *(double *)param_2 = local_10;
        bVar1 = bVar3;
      }
      if (bVar1) {
        CDXTexture__Helper_00562c99();
      }
      uVar2 = param_1 & 0x1d;
    }
    goto LAB_005629df;
  }
  CDXTexture__Helper_00562c99();
  uVar2 = param_3 & 0xc00;
  dVar4 = _DAT_00653840;
  if (uVar2 == 0) {
    if (*(double *)param_2 <= _DAT_005d87b0) {
      dVar4 = -_DAT_00653840;
    }
LAB_005628ff:
    *(double *)param_2 = dVar4;
  }
  else {
    if (uVar2 == 0x400) {
      dVar4 = _DAT_00653850;
      if (*(double *)param_2 <= _DAT_005d87b0) {
        dVar4 = -_DAT_00653840;
      }
      goto LAB_005628ff;
    }
    if (uVar2 == 0x800) {
      if (*(double *)param_2 <= _DAT_005d87b0) {
        dVar4 = -_DAT_00653850;
      }
      goto LAB_005628ff;
    }
    if (uVar2 == 0xc00) {
      dVar4 = _DAT_00653850;
      if (*(double *)param_2 <= _DAT_005d87b0) {
        dVar4 = -_DAT_00653850;
      }
      goto LAB_005628ff;
    }
  }
  uVar2 = param_1 & 0x1e;
LAB_005629df:
  if (((param_1 & 0x10) != 0) && ((param_3 & 0x20) != 0)) {
    CDXTexture__Helper_00562c99();
    uVar2 = uVar2 & 0xffffffef;
  }
  return uVar2 == 0;
}
