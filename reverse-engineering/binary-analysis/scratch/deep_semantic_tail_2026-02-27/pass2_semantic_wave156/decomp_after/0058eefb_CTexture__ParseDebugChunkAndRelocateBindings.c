/* address: 0x0058eefb */
/* name: CTexture__ParseDebugChunkAndRelocateBindings */
/* signature: int __fastcall CTexture__ParseDebugChunkAndRelocateBindings(void * param_1) */


int __fastcall CTexture__ParseDebugChunkAndRelocateBindings(void *param_1)

{
  int iVar1;
  undefined4 *extraout_EAX;
  undefined4 *extraout_EAX_00;
  void *pvVar2;
  int *piVar3;
  int iVar4;
  uint uVar5;
  undefined2 *puVar6;
  void *unaff_EDI;
  uint *puVar7;
  undefined4 *puVar8;
  int iVar9;
  uint local_54 [5];
  uint local_40;
  undefined1 local_2c [16];
  uint local_1c;
  int local_18;
  uint local_14;
  undefined4 *local_10;
  undefined4 *local_c;
  int local_8;

  CTexture__Unk_00598fdc(local_2c,(void *)0x47554244,(int)unaff_EDI);
  puVar7 = local_54;
  for (iVar4 = 10; iVar4 != 0; iVar4 = iVar4 + -1) {
    *puVar7 = 0;
    puVar7 = puVar7 + 1;
  }
  iVar4 = 0;
  local_54[0] = 0x28;
  local_10 = (undefined4 *)0x0;
  local_c = (undefined4 *)0x0;
  local_8 = CDXTexture__Helper_0059902a();
  if (local_8 < 0) goto LAB_0058f1be;
  for (iVar1 = *(int *)((int)param_1 + 0x34); iVar9 = iVar4, iVar1 != 0;
      iVar1 = *(int *)(iVar1 + 0xc)) {
    if ((*(int *)(iVar1 + 8) != 0) && (*(int *)(*(int *)(iVar1 + 8) + 4) == 0x11)) {
      iVar4 = *(int *)(iVar1 + 8);
      iVar9 = iVar4;
      break;
    }
  }
  for (; iVar4 != 0; iVar4 = *(int *)(iVar4 + 0xc)) {
    local_40 = local_40 + 1;
  }
  if (local_40 == 0) {
LAB_0058f09c:
    if ((((*(int *)((int)param_1 + 0x74) == 0) ||
         (local_8 = CDXTexture__Helper_0059902a(), -1 < local_8)) &&
        ((*(int *)((int)param_1 + 0x6c) == 0 ||
         ((iVar4 = CDXTexture__Helper_0059902a(), -1 < iVar4 &&
          (iVar4 = CDXTexture__Helper_0059902a(), -1 < iVar4)))))) &&
       (iVar4 = CDXTexture__Helper_0059902a(), -1 < iVar4)) {
      pvVar2 = (void *)CTexture__Helper_00599161((int)local_2c);
      if (pvVar2 < (void *)0x8001) {
        local_8 = CTexture__Helper_0058e413(param_1,(int)pvVar2,(int)unaff_EDI);
        if (local_8 < 0) goto LAB_0058f1be;
        CDXTexture__Helper_0055ed50
                  ((void *)(*(int *)((int)param_1 + 0x58) + 4 + (int)pvVar2 * 4),
                   (void *)(*(int *)((int)param_1 + 0x58) + 4),*(int *)((int)param_1 + 0x5c) * 4 - 4
                  );
        uVar5 = 0;
        if (local_40 != 0) {
          piVar3 = local_c + 1;
          do {
            *piVar3 = *piVar3 + (*(int *)((int)param_1 + 0x68) + (int)pvVar2) * 4;
            uVar5 = uVar5 + 1;
            piVar3 = piVar3 + 2;
          } while (uVar5 < local_40);
        }
        local_8 = CTexture__Helper_0059916d
                            (local_2c,(void *)(*(int *)((int)param_1 + 0x58) + 4),pvVar2,unaff_EDI);
        if (local_8 < 0) goto LAB_0058f1be;
        *(int *)((int)param_1 + 0x5c) = *(int *)((int)param_1 + 0x5c) + (int)pvVar2;
        *(int *)((int)param_1 + 0x68) = *(int *)((int)param_1 + 0x68) + (int)pvVar2;
        *(undefined4 *)((int)param_1 + 100) = *(undefined4 *)((int)param_1 + 0x5c);
      }
      else {
        CTexture__Helper_0058c95c(*(void **)param_1,(int)param_1 + 0x10,0x7ee);
      }
      local_8 = 0;
    }
  }
  else {
    CFastVB__Helper_00426fd0(local_40 << 2);
    uVar5 = local_40;
    puVar8 = extraout_EAX;
    local_10 = extraout_EAX;
    if (extraout_EAX != (undefined4 *)0x0) {
      for (; uVar5 != 0; uVar5 = uVar5 - 1) {
        *puVar8 = 0;
        puVar8 = puVar8 + 1;
      }
      CFastVB__Helper_00426fd0(local_40 << 3);
      local_c = extraout_EAX_00;
      if (extraout_EAX_00 != (undefined4 *)0x0) {
        local_1c = local_40 << 3;
        puVar8 = extraout_EAX_00;
        for (uVar5 = local_1c >> 2; uVar5 != 0; uVar5 = uVar5 - 1) {
          *puVar8 = 0;
          puVar8 = puVar8 + 1;
        }
        for (iVar4 = 0; iVar4 != 0; iVar4 = iVar4 + -1) {
          *(undefined1 *)puVar8 = 0;
          puVar8 = (undefined4 *)((int)puVar8 + 1);
        }
        if (iVar9 != 0) {
          puVar6 = (undefined2 *)((int)extraout_EAX_00 + local_40 * 8 + -6);
          do {
            *puVar6 = 0xffff;
            puVar6[-1] = *(undefined2 *)(iVar9 + 0x24);
            *(undefined4 *)(puVar6 + 1) = *(undefined4 *)(iVar9 + 0x58);
            if (*(int *)(iVar9 + 0x20) != 0) {
              iVar4 = CDXTexture__Helper_0059902a();
              if (iVar4 < 0) goto LAB_0058f1be;
              local_14 = 0;
              if (local_54[3] != 0) {
                do {
                  if (local_10[local_14] == local_18) break;
                  local_14 = local_14 + 1;
                } while (local_14 < local_54[3]);
              }
              if (local_14 == local_54[3]) {
                local_10[local_54[3]] = local_18;
                local_54[3] = local_54[3] + 1;
              }
              *puVar6 = (short)local_14;
            }
            iVar9 = *(int *)(iVar9 + 0xc);
            puVar6 = puVar6 + -4;
          } while (iVar9 != 0);
        }
        if (((local_54[3] != 0) && (local_8 = CDXTexture__Helper_0059902a(), local_8 < 0)) ||
           (local_8 = CDXTexture__Helper_0059902a(), local_8 < 0)) goto LAB_0058f1be;
        goto LAB_0058f09c;
      }
    }
    local_8 = -0x7ff8fff2;
  }
LAB_0058f1be:
  OID__FreeObject_Callback(local_10);
  OID__FreeObject_Callback(local_c);
  CTexture__Unk_00598ff4((int)local_2c);
  return local_8;
}
