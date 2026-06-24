/* address: 0x005876ab */
/* name: CTexture__Unk_005876ab */
/* signature: void __thiscall CTexture__Unk_005876ab(void * this, void * param_1, uint param_2, int param_3, void * param_4) */


void __thiscall
CTexture__Unk_005876ab(void *this,void *param_1,uint param_2,int param_3,void *param_4)

{
  undefined4 *extraout_EAX;
  void *extraout_EAX_00;
  uint uVar1;
  uint uVar2;
  int iVar3;
  void *pvVar4;
  int unaff_ESI;
  uint *puVar5;
  undefined4 *puVar6;
  int iVar7;
  undefined4 *puVar8;
  uint local_24 [4];
  void *local_14;
  uint local_10;
  uint local_c;
  uint *local_8;

  uVar1 = (int)param_1 + *(int *)((int)this + 0x103c);
  iVar7 = param_2 + *(int *)((int)this + 0x1048);
  if (*(int *)((int)this + 0x10ec) == 0) {
    CFastVB__Helper_00426fd0(*(int *)((int)this + 0x10d4) * *(int *)((int)this + 0x10d8) * 8);
    *(undefined4 **)((int)this + 0x10ec) = extraout_EAX;
    if (extraout_EAX == (undefined4 *)0x0) {
      return;
    }
    puVar6 = extraout_EAX;
    for (uVar2 = (uint)(*(int *)((int)this + 0x10d4) * *(int *)((int)this + 0x10d8) * 8) >> 2;
        uVar2 != 0; uVar2 = uVar2 - 1) {
      *puVar6 = 0;
      puVar6 = puVar6 + 1;
    }
    for (iVar3 = 0; iVar3 != 0; iVar3 = iVar3 + -1) {
      *(undefined1 *)puVar6 = 0;
      puVar6 = (undefined4 *)((int)puVar6 + 1);
    }
  }
  puVar5 = (uint *)(*(int *)((int)this + 0x10ec) +
                   ((iVar7 - *(int *)((int)this + 0x10c8)) * *(int *)((int)this + 0x10d4) +
                   (uVar1 - *(int *)((int)this + 0x10bc) >> 2)) * 8);
  local_8 = puVar5;
  if (puVar5[1] == 0) {
    iVar3 = *(int *)((int)this + 0x10d0);
    CFastVB__Helper_00426fd0(iVar3 << 8);
    local_14 = extraout_EAX_00;
    if (extraout_EAX_00 == (void *)0x0) {
      pvVar4 = (void *)0x0;
    }
    else {
      _vector_constructor_iterator_(extraout_EAX_00,0x10,iVar3 << 4,CFastVB__Helper_00574577);
      pvVar4 = local_14;
    }
    puVar5[1] = (uint)pvVar4;
    if (pvVar4 == (void *)0x0) {
      return;
    }
    *puVar5 = 0;
    *(int *)((int)this + 0x10e8) = *(int *)((int)this + 0x10e8) + 1;
  }
  if (*puVar5 == 0) {
    local_14 = (void *)(uVar1 & 0xfffffffc);
    if (((local_14 < *(void **)((int)this + 0x103c)) &&
        (*(void **)((int)this + 0x108c) < *(void **)((int)this + 0x103c))) ||
       ((*(uint *)((int)this + 0x1044) < (int)local_14 + 4U &&
        (*(uint *)((int)this + 0x1044) < *(uint *)((int)this + 0x1094))))) {
      local_10 = *(uint *)((int)this + 0x10b8);
      iVar3 = (uVar1 >> 2) * *(int *)((int)this + 0x1058) +
              (local_10 >> 2) * *(int *)((int)this + 0x107c) + *(int *)((int)this + 0x105c) * iVar7
              + *(int *)((int)this + 0x20);
      local_c = puVar5[1];
      if (local_10 < *(uint *)((int)this + 0x10c0)) {
        do {
          (**(code **)((int)this + 0x1080))(local_c,iVar3);
          local_10 = local_10 + 4;
          iVar3 = iVar3 + *(int *)((int)this + 0x107c);
          local_c = local_c + 0x100;
        } while (local_10 < *(uint *)((int)this + 0x10c0));
      }
    }
    else {
      if ((*(uint *)((int)this + 0x10b8) < *(uint *)((int)this + 0x1038)) &&
         (*(uint *)((int)this + 0x1088) < *(uint *)((int)this + 0x1038))) {
        (**(code **)((int)this + 0x1080))
                  (puVar5[1],
                   (*(uint *)((int)this + 0x10b8) >> 2) * *(int *)((int)this + 0x107c) +
                   (uVar1 >> 2) * *(int *)((int)this + 0x1058) +
                   *(int *)((int)this + 0x105c) * iVar7 + *(int *)((int)this + 0x20));
      }
      if ((*(uint *)((int)this + 0x1040) < *(uint *)((int)this + 0x10c0)) &&
         (*(uint *)((int)this + 0x1040) < *(uint *)((int)this + 0x1090))) {
        (**(code **)((int)this + 0x1080))
                  (puVar5[1],
                   (*(uint *)((int)this + 0x10c0) - 4 >> 2) * *(int *)((int)this + 0x107c) +
                   (uVar1 >> 2) * *(int *)((int)this + 0x1058) +
                   *(int *)((int)this + 0x105c) * iVar7 + *(int *)((int)this + 0x20));
      }
    }
    uVar2 = 0;
    do {
      if ((uVar2 + (int)local_14 < *(uint *)((int)this + 0x103c)) ||
         (*(uint *)((int)this + 0x1044) <= uVar2 + (int)local_14)) {
        *puVar5 = *puVar5 | 1 << ((byte)uVar2 & 0x1f);
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 4);
  }
  if (*(int *)((int)this + 0x1050) != 0) {
    param_3 = CFastVB__Helper_00581279(this,param_3,unaff_ESI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    param_3 = CDXTexture__Helper_00581e8c(this,param_3,unaff_ESI);
  }
  uVar2 = *(int *)((int)this + 0x1038) - *(int *)((int)this + 0x10b8);
  iVar3 = *(int *)((int)this + 0x10bc);
  local_14 = (void *)(*(int *)((int)this + 0x1060) + uVar2);
  for (; uVar2 < local_14; uVar2 = uVar2 + 1) {
    puVar6 = (undefined4 *)
             (((uVar2 & 0xfffffffc | uVar1 - iVar3 & 3) << 2 | uVar2 & 3) * 0x10 + puVar5[1]);
    *puVar6 = *(undefined4 *)param_3;
    puVar6[1] = *(undefined4 *)(param_3 + 4);
    puVar6[2] = *(undefined4 *)(param_3 + 8);
    puVar6[3] = *(undefined4 *)(param_3 + 0xc);
    puVar5 = local_8;
    param_3 = (int)(param_3 + 0x10);
  }
  *puVar5 = *puVar5 | 1 << ((byte)uVar1 & 3);
  if (*puVar5 == 0xf) {
    local_c = *(uint *)((int)this + 0x10b8);
    iVar7 = (uVar1 >> 2) * *(int *)((int)this + 0x1058) +
            (local_c >> 2) * *(int *)((int)this + 0x107c) + *(int *)((int)this + 0x105c) * iVar7 +
            *(int *)((int)this + 0x20);
    param_3 = puVar5[1];
    if (local_c < *(uint *)((int)this + 0x10c0)) {
      local_24[0] = 0;
      local_24[1] = 0;
      local_24[2] = 0;
      local_14 = (void *)(uVar1 & 0xfffffffc);
      local_24[3] = 1;
      do {
        uVar1 = *(int *)((int)this + 0x1090) - local_c;
        pvVar4 = (void *)(*(int *)((int)this + 0x1094) - (int)local_14);
        if ((uVar1 < 4) && (param_1 = (void *)0x0, pvVar4 != (void *)0x0)) {
          do {
            uVar2 = uVar1;
            if ((void *)0x3 < param_1) break;
            do {
              puVar6 = (undefined4 *)((local_24[uVar2] | (int)param_1 << 2) * 0x10 + param_3);
              puVar8 = (undefined4 *)(((int)param_1 << 2 | uVar2) * 0x10 + param_3);
              uVar2 = uVar2 + 1;
              *puVar8 = *puVar6;
              puVar8[1] = puVar6[1];
              puVar8[2] = puVar6[2];
              puVar8[3] = puVar6[3];
            } while (uVar2 < 4);
            param_1 = (void *)((int)param_1 + 1);
            puVar5 = local_8;
          } while (param_1 < pvVar4);
        }
        for (; pvVar4 < (void *)0x4; pvVar4 = (void *)((int)pvVar4 + 1)) {
          uVar1 = local_24[(int)pvVar4];
          uVar2 = 0;
          do {
            puVar8 = (undefined4 *)(((int)pvVar4 << 2 | uVar2) * 0x10 + param_3);
            puVar6 = (undefined4 *)((uVar1 << 2 | uVar2) * 0x10 + param_3);
            uVar2 = uVar2 + 1;
            *puVar8 = *puVar6;
            puVar8[1] = puVar6[1];
            puVar8[2] = puVar6[2];
            puVar8[3] = puVar6[3];
          } while (uVar2 < 4);
          puVar5 = local_8;
        }
        (**(code **)((int)this + 0x1084))(iVar7,param_3);
        local_c = local_c + 4;
        iVar7 = iVar7 + *(int *)((int)this + 0x107c);
        param_3 = param_3 + 0x100;
      } while (local_c < *(uint *)((int)this + 0x10c0));
    }
    if (((puVar5 + 2 <
          (uint *)(*(int *)((int)this + 0x10ec) +
                  *(int *)((int)this + 0x10d8) * *(int *)((int)this + 0x10d4) * 8)) &&
        (puVar5[2] == 0)) && (puVar5[3] == 0)) {
      puVar5[3] = puVar5[1];
      puVar5[1] = 0;
    }
    else {
      OID__FreeObject_Callback((void *)puVar5[1]);
      *(int *)((int)this + 0x10e8) = *(int *)((int)this + 0x10e8) + -1;
    }
    puVar5[1] = 0;
  }
  return;
}
