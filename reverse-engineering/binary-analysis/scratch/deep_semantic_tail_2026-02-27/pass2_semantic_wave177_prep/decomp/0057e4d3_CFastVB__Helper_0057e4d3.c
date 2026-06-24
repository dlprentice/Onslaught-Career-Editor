/* address: 0x0057e4d3 */
/* name: CFastVB__Helper_0057e4d3 */
/* signature: int __fastcall CFastVB__Helper_0057e4d3(void * param_1) */


int __fastcall CFastVB__Helper_0057e4d3(void *param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  void *extraout_EAX;
  undefined4 *extraout_EAX_00;
  uint uVar6;
  undefined4 *puVar7;
  undefined4 *puVar8;
  uint uVar9;
  uint local_28;
  uint local_24;
  uint local_20;
  uint local_1c;
  uint local_18;
  uint local_14;
  uint local_10;
  undefined4 *local_c;
  void *local_8;

  if (*(char *)((int)param_1 + 8) == '\x02') {
    iVar5 = *(int *)(*(int *)param_1 + 0x1060);
    OID__AllocObject_DefaultTag_00662b2c(iVar5 << 4);
    if (extraout_EAX == (void *)0x0) {
      local_8 = (void *)0x0;
    }
    else {
      _vector_constructor_iterator_(extraout_EAX,0x10,iVar5,CFastVB__ReturnInputInt);
      local_8 = extraout_EAX;
    }
    if (local_8 == (void *)0x0) {
      iVar5 = -0x7ff8fff2;
    }
    else {
      iVar5 = *(int *)(*(int *)((int)param_1 + 4) + 0x1060);
      OID__AllocObject_DefaultTag_00662b2c(iVar5 << 4);
      if (extraout_EAX_00 == (undefined4 *)0x0) {
        local_c = (undefined4 *)0x0;
      }
      else {
        _vector_constructor_iterator_(extraout_EAX_00,0x10,iVar5,CFastVB__ReturnInputInt);
        local_c = extraout_EAX_00;
      }
      if (local_c == (undefined4 *)0x0) {
        OID__FreeObject_Callback(local_8);
        iVar5 = -0x7ff8fff2;
      }
      else {
        if ((*(int *)(*(int *)((int)param_1 + 4) + 0x10) != 0) &&
           (*(int *)(*(int *)param_1 + 0x10) != 0)) {
          *(undefined4 *)(*(int *)((int)param_1 + 4) + 0x10) = 0;
          *(undefined4 *)(*(int *)param_1 + 0x10) = 0;
        }
        iVar5 = *(int *)param_1;
        iVar1 = *(int *)((int)param_1 + 4);
        iVar2 = *(int *)(iVar5 + 0x1060);
        uVar3 = *(uint *)(iVar1 + 0x1060);
        uVar9 = *(uint *)(iVar1 + 0x1064);
        uVar4 = *(uint *)(iVar1 + 0x1068);
        local_20 = 0;
        local_14 = 0;
        uVar6 = (uint)(*(int *)(iVar5 + 0x1064) << 0x10) / uVar9;
        iVar5 = *(int *)(iVar5 + 0x1068);
        if (uVar4 != 0) {
          do {
            local_24 = 0xffffffff;
            local_28 = 0;
            local_10 = 0;
            if (uVar9 != 0) {
              do {
                local_18 = 0;
                local_1c = 0;
                if (((local_24 ^ local_28) & 0xffff0000) != 0) {
                  (**(code **)(**(int **)param_1 + 4))(local_28 >> 0x10,local_20 >> 0x10,local_8);
                  local_24 = local_28;
                }
                puVar7 = local_c;
                if (*(int *)(*(int *)((int)param_1 + 4) + 0x1060) != 0) {
                  do {
                    puVar8 = (undefined4 *)((local_18 >> 0x10) * 0x10 + (int)local_8);
                    local_1c = local_1c + 1;
                    *puVar7 = *puVar8;
                    puVar7[1] = puVar8[1];
                    puVar7[2] = puVar8[2];
                    puVar7[3] = puVar8[3];
                    puVar7 = puVar7 + 4;
                    local_18 = local_18 + (uint)(iVar2 << 0x10) / uVar3;
                  } while (local_1c < *(uint *)(*(int *)((int)param_1 + 4) + 0x1060));
                }
                (**(code **)(**(int **)((int)param_1 + 4) + 8))(local_10,local_14,local_c);
                local_28 = local_28 + uVar6;
                local_10 = local_10 + 1;
                uVar9 = *(uint *)(*(int *)((int)param_1 + 4) + 0x1064);
              } while (local_10 < uVar9);
            }
            local_20 = local_20 + (uint)(iVar5 << 0x10) / uVar4;
            local_14 = local_14 + 1;
          } while (local_14 < *(uint *)(*(int *)((int)param_1 + 4) + 0x1068));
        }
        OID__FreeObject_Callback(local_8);
        OID__FreeObject_Callback(local_c);
        iVar5 = 0;
      }
    }
  }
  else {
    iVar5 = -0x7fffbffb;
  }
  return iVar5;
}
