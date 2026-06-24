/* address: 0x0057e2de */
/* name: CFastVB__Unk_0057e2de */
/* signature: int __fastcall CFastVB__Unk_0057e2de(void * param_1) */


int __fastcall CFastVB__Unk_0057e2de(void *param_1)

{
  int iVar1;
  int iVar2;
  undefined4 *extraout_EAX;
  undefined4 *extraout_EAX_00;
  int *piVar3;
  uint uVar4;
  undefined4 *puVar5;
  uint uVar6;
  uint local_18;
  uint local_14;
  undefined4 *local_10;
  uint local_c;
  undefined4 *local_8;

  if (*(char *)((int)param_1 + 8) == '\x01') {
    iVar2 = *(int *)((int)param_1 + 4);
    iVar1 = *(int *)param_1;
    local_10 = (undefined4 *)*(uint *)(iVar2 + 0x1060);
    if (*(uint *)(iVar2 + 0x1060) <= *(uint *)(iVar1 + 0x1060)) {
      local_10 = (undefined4 *)*(uint *)(iVar1 + 0x1060);
    }
    local_18 = *(uint *)(iVar2 + 0x1064);
    if (*(uint *)(iVar1 + 0x1064) <= *(uint *)(iVar2 + 0x1064)) {
      local_18 = *(uint *)(iVar1 + 0x1064);
    }
    local_14 = *(uint *)(iVar2 + 0x1068);
    if (*(uint *)(iVar1 + 0x1068) <= *(uint *)(iVar2 + 0x1068)) {
      local_14 = *(uint *)(iVar1 + 0x1068);
    }
    uVar4 = (int)local_10 << 4;
    CFastVB__Helper_00426fd0(uVar4);
    if (extraout_EAX == (undefined4 *)0x0) {
      local_8 = (undefined4 *)0x0;
    }
    else {
      _vector_constructor_iterator_(extraout_EAX,0x10,(int)local_10,CFastVB__Helper_00574577);
      local_8 = extraout_EAX;
    }
    if (local_8 == (undefined4 *)0x0) {
      iVar2 = -0x7fffbffb;
    }
    else {
      iVar2 = *(int *)(*(int *)((int)param_1 + 4) + 0x1060);
      CFastVB__Helper_00426fd0(iVar2 << 4);
      if (extraout_EAX_00 == (undefined4 *)0x0) {
        local_10 = (undefined4 *)0x0;
      }
      else {
        _vector_constructor_iterator_(extraout_EAX_00,0x10,iVar2,CFastVB__Helper_00574577);
        local_10 = extraout_EAX_00;
      }
      if (local_10 == (undefined4 *)0x0) {
        OID__FreeObject_Callback(local_8);
        iVar2 = -0x7fffbffb;
      }
      else {
        puVar5 = local_8;
        for (uVar4 = uVar4 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
          *puVar5 = 0;
          puVar5 = puVar5 + 1;
        }
        for (iVar2 = 0; iVar2 != 0; iVar2 = iVar2 + -1) {
          *(undefined1 *)puVar5 = 0;
          puVar5 = (undefined4 *)((int)puVar5 + 1);
        }
        puVar5 = local_10;
        for (uVar4 = (uint)(*(int *)(*(int *)((int)param_1 + 4) + 0x1060) << 4) >> 2; uVar4 != 0;
            uVar4 = uVar4 - 1) {
          *puVar5 = 0;
          puVar5 = puVar5 + 1;
        }
        for (iVar2 = 0; iVar2 != 0; iVar2 = iVar2 + -1) {
          *(undefined1 *)puVar5 = 0;
          puVar5 = (undefined4 *)((int)puVar5 + 1);
        }
        if ((*(int *)(*(int *)((int)param_1 + 4) + 0x10) != 0) &&
           (*(int *)(*(int *)param_1 + 0x10) != 0)) {
          *(undefined4 *)(*(int *)((int)param_1 + 4) + 0x10) = 0;
          *(undefined4 *)(*(int *)param_1 + 0x10) = 0;
        }
        local_c = 0;
        if (local_14 != 0) {
          do {
            uVar4 = 0;
            if (local_18 != 0) {
              do {
                (**(code **)(**(int **)param_1 + 4))(uVar4,local_c,local_8);
                (**(code **)(**(int **)((int)param_1 + 4) + 8))(uVar4,local_c,local_8);
                uVar4 = uVar4 + 1;
              } while (uVar4 < local_18);
            }
            piVar3 = *(int **)((int)param_1 + 4);
            uVar4 = local_18;
            if (local_18 < (uint)piVar3[0x419]) {
              do {
                (**(code **)(*piVar3 + 8))(uVar4,local_c,local_10);
                piVar3 = *(int **)((int)param_1 + 4);
                uVar4 = uVar4 + 1;
              } while (uVar4 < (uint)piVar3[0x419]);
            }
            local_c = local_c + 1;
          } while (local_c < local_14);
        }
        piVar3 = *(int **)((int)param_1 + 4);
        if (local_14 < (uint)piVar3[0x41a]) {
          uVar4 = piVar3[0x419];
          do {
            uVar6 = 0;
            if (uVar4 != 0) {
              do {
                (**(code **)(*piVar3 + 8))(uVar6,local_14,local_10);
                piVar3 = *(int **)((int)param_1 + 4);
                uVar4 = piVar3[0x419];
                uVar6 = uVar6 + 1;
              } while (uVar6 < uVar4);
            }
            piVar3 = *(int **)((int)param_1 + 4);
            local_14 = local_14 + 1;
          } while (local_14 < (uint)piVar3[0x41a]);
        }
        OID__FreeObject_Callback(local_8);
        OID__FreeObject_Callback(local_10);
        iVar2 = 0;
      }
    }
  }
  else {
    iVar2 = -0x7fffbffb;
  }
  return iVar2;
}
