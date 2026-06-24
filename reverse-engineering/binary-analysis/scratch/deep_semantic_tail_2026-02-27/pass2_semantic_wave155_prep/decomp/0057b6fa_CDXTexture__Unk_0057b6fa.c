/* address: 0x0057b6fa */
/* name: CDXTexture__Unk_0057b6fa */
/* signature: uint __thiscall CDXTexture__Unk_0057b6fa(void * this, void * param_1, void * param_2, uint param_3) */


uint __thiscall CDXTexture__Unk_0057b6fa(void *this,void *param_1,void *param_2,uint param_3)

{
  byte bVar1;
  bool bVar2;
  byte *pbVar3;
  uint uVar4;
  uint *puVar5;
  uint uVar6;
  void *extraout_EAX;
  uint *puVar7;
  uint uVar8;
  int unaff_EDI;
  byte *pbVar9;
  int iVar10;
  uint local_18;
  uint *local_14;
  uint local_c;
  int local_8;

  if (param_2 < (void *)0x2) {
    return 0x80004005;
  }
  if (*(char *)param_1 == 'P') {
    if (*(char *)((int)param_1 + 1) == '3') {
      bVar2 = true;
    }
    else {
      if (*(char *)((int)param_1 + 1) != '6') {
        return 0x80004005;
      }
      bVar2 = false;
    }
    pbVar9 = (byte *)((int)param_1 + 2);
    param_2 = (void *)((int)param_2 - 2);
    local_8 = 0;
    local_18 = 0;
    local_c = 0xff;
    pbVar3 = pbVar9;
    puVar7 = this;
    while (param_2 != (void *)0x0) {
      uVar8 = 0;
      if ((!bVar2) && (local_8 == 3)) {
        if (0xff < local_c) {
          return 0x80004005;
        }
        if (((void *)0x1 < param_2) && (*pbVar9 == 0xd)) {
          pbVar9 = pbVar9 + 1;
          param_2 = (void *)((int)param_2 - 1);
        }
        iVar10 = (int)param_2 + -1;
        pbVar9 = pbVar9 + 1;
        for (; (iVar10 != 0 && (param_1 < local_14)); param_1 = (void *)((int)param_1 + 4)) {
          *(uint *)param_1 =
               ((((uint)*pbVar9 * 0xff) / local_c | 0xffffff00) << 8 |
               ((uint)pbVar9[1] * 0xff) / local_c) << 8 | ((uint)pbVar9[2] * 0xff) / local_c;
          iVar10 = iVar10 + -3;
          pbVar9 = pbVar9 + 3;
        }
        return -(uint)(param_1 != local_14) & 0x80004005;
      }
      puVar5 = (uint *)(uint)*pbVar9;
      uVar6 = CDXTexture__Helper_0056a0de(puVar7,puVar5,unaff_EDI);
      puVar7 = puVar5;
      if (uVar6 == 0) {
        if (*pbVar9 == 0x23) {
          for (; (param_2 != (void *)0x0 && (*pbVar9 != 10)); pbVar9 = pbVar9 + 1) {
            param_2 = (void *)((int)param_2 - 1);
          }
          goto LAB_0057b784;
        }
        for (; param_2 != (void *)0x0; param_2 = (void *)((int)param_2 - 1)) {
          puVar5 = (uint *)(uint)*pbVar9;
          uVar6 = CDXTexture__Helper_0056a0de(puVar7,(uint *)(uint)*pbVar9,unaff_EDI);
          puVar7 = puVar5;
          if (uVar6 != 0) break;
          uVar6 = CTexture__Helper_0056a089(puVar7,(void *)(uint)*pbVar9,unaff_EDI);
          if (uVar6 == 0) {
            return 0x80004005;
          }
          bVar1 = *pbVar9;
          pbVar9 = pbVar9 + 1;
          uVar8 = (int)(uint)bVar1 + uVar8 * 10 + -0x30;
          puVar7 = (uint *)(uint)bVar1;
          pbVar3 = pbVar9;
        }
        uVar6 = uVar8;
        uVar4 = local_c;
        if (local_8 == 0) {
LAB_0057b8c9:
          local_c = uVar4;
          local_18 = uVar6;
          if (uVar8 == 0) {
            return 0x80004005;
          }
        }
        else if (local_8 == 1) {
          if (uVar8 == 0) {
            return 0x80004005;
          }
          iVar10 = uVar8 * local_18 * 4;
          CFastVB__Helper_00426fd0(iVar10);
          *(void **)((int)this + 4) = extraout_EAX;
          if (extraout_EAX == (void *)0x0) {
            return 0x8007000e;
          }
          local_14 = (uint *)(iVar10 + (int)extraout_EAX);
          puVar7 = (uint *)0x1;
          *(undefined4 *)((int)this + 0x34) = 0;
          *(undefined4 *)((int)this + 0x38) = 1;
          *(undefined4 *)this = 0x16;
          *(uint *)((int)this + 0x30) = local_18 << 2;
          *(uint *)((int)this + 0xc) = local_18;
          *(uint *)((int)this + 0x10) = uVar8;
          *(undefined4 *)((int)this + 0x14) = 1;
          pbVar9 = pbVar3;
          param_1 = extraout_EAX;
        }
        else {
          uVar6 = local_18;
          uVar4 = uVar8;
          if (local_8 == 2) goto LAB_0057b8c9;
          if (local_8 == 3) {
            if (local_14 <= param_1) {
              return 0x80004005;
            }
            *(uint *)param_1 = ((uVar8 * 0xff) / local_c | 0xffffff00) << 0x10;
            puVar7 = param_1;
          }
          else if (local_8 == 4) {
            puVar7 = (uint *)((uVar8 * 0xff) / local_c << 8);
            *(uint *)param_1 = *(uint *)param_1 | (uint)puVar7;
          }
          else if (local_8 == 5) {
            *(uint *)param_1 = *(uint *)param_1 | (uVar8 * 0xff) / local_c;
            param_1 = (void *)((int)param_1 + 4);
            if (param_1 == local_14) {
              return 0;
            }
            local_8 = 2;
            puVar7 = param_1;
          }
        }
        local_8 = local_8 + 1;
      }
      else {
LAB_0057b784:
        pbVar9 = pbVar9 + 1;
        param_2 = (void *)((int)param_2 - 1);
        pbVar3 = pbVar9;
      }
    }
  }
  return 0x80004005;
}
