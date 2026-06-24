/* address: 0x00507ab0 */
/* name: OID__CanFireAtTarget_BallisticArcA */
/* signature: int __thiscall OID__CanFireAtTarget_BallisticArcA(void * this, void * param_1, int param_2, int param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall OID__CanFireAtTarget_BallisticArcA(void *this,void *param_1,int param_2,int param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  int iVar5;
  float fVar6;
  float fVar7;
  bool bVar8;
  void *pvVar9;
  float fVar10;
  int extraout_EAX;
  int iVar11;
  void *this_00;
  float *extraout_EAX_00;
  undefined4 *extraout_EAX_01;
  void *this_01;
  float *extraout_EAX_02;
  undefined4 *extraout_EAX_03;
  float *extraout_EAX_04;
  undefined4 *extraout_EAX_05;
  undefined4 *extraout_EAX_06;
  void *pvVar12;
  void *unaff_EDI;
  float10 extraout_ST0;
  float10 extraout_ST0_00;
  float10 fVar13;
  float10 extraout_ST0_01;
  float10 fVar14;
  float10 fVar15;
  double dVar16;
  int in_stack_fffffddc;
  undefined1 *puVar17;
  float local_1b4;
  float local_1b0;
  float local_1ac;
  float local_19c;
  float local_198;
  float local_194;
  undefined4 local_190;
  float local_18c;
  float local_188;
  float local_184;
  undefined4 local_180;
  undefined4 local_17c;
  undefined4 local_178;
  float local_174;
  undefined4 local_170;
  float local_16c;
  float local_168;
  int local_15c [4];
  undefined **local_14c;
  float local_148;
  float local_138;
  undefined4 local_134;
  undefined4 local_130;
  undefined4 local_12c;
  float local_128;
  float local_124;
  float local_120;
  undefined4 local_11c;
  undefined1 local_118 [4];
  float local_114;
  float local_104;
  float local_f4;
  float local_e8;
  float local_e4;
  undefined **local_d8;
  undefined4 local_d4;
  undefined4 local_d0;
  undefined4 local_cc;
  undefined4 local_c4;
  undefined4 local_c0;
  undefined4 local_bc;
  undefined4 local_b8;
  undefined4 local_b4;
  undefined4 local_b0;
  float local_ac;
  undefined4 local_a8;
  undefined **local_a4 [5];
  undefined4 local_90;
  undefined4 local_8c;
  undefined4 local_88;
  undefined4 local_84;
  float local_80;
  float local_7c;
  float local_78;
  undefined4 local_74;
  undefined **local_70 [5];
  undefined4 local_5c;
  undefined4 local_58;
  undefined4 local_54;
  undefined4 local_50;
  float local_4c;
  float local_48;
  float local_44;
  undefined4 local_40;
  undefined1 local_3c [16];
  undefined1 local_2c [16];
  undefined1 local_1c [16];
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  fVar1 = DAT_006fbdfc;
  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d5959;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  OID__Helper_0044a850(this,(int)&local_19c,unaff_EDI);
  if ((*(float *)(extraout_EAX + 8) <= fVar1) &&
     ((((((*(int *)((int)this + 0xa0) == 0 ||
          (iVar11 = *(int *)(*(int *)((int)this + 0xa0) + 0x18), iVar11 == 0)) ||
         (*(int *)(iVar11 + 0x58) == 0)) ||
        ((iVar11 = *(int *)(*(int *)((int)this + 8) + 0x138), pvVar12 = DAT_008a9d7c, iVar11 != 0 &&
         (pvVar12 = DAT_008a9d80, iVar11 != 1)))) || (pvVar12 == (void *)0x0)) ||
      (iVar11 = OID__Helper_0044c780
                          (pvVar12,*(int *)((int)param_1 + 0x1c),*(float *)((int)param_1 + 0x20),
                           *(float *)((int)param_1 + 0x24),*(float *)((int)param_1 + 0x28)),
      iVar11 != 0)))) {
    OID__Helper_0044a930(this,(int)&local_14c,unaff_EDI);
    Vec3__SetXYZ();
    if (*(int *)((int)this + 0x94) != 0) {
      puVar17 = local_118;
      pvVar12 = (void *)(*(int *)((int)this + 8) + 0x3c);
      OID__Helper_0040d1f0
                (&local_14c,*(void **)(*(int *)((int)this + 8) + 0xe0),0.0,0.0,(float)puVar17);
      CMCBuggy__Helper_0040d320(this_00,puVar17,pvVar12,unaff_EDI);
      Vec3__SetXYZ();
      local_e4 = local_198;
      local_e8 = local_19c;
    }
    fVar15 = (float10)fpatan((float10)local_e8,(float10)local_e4);
    pvVar12 = (void *)(float)-fVar15;
    if (*(int *)((int)this + 0x98) == 0) {
      dVar16 = SQRT__Wrapper_004026b0(&local_e8);
      if ((float)dVar16 <= _DAT_005d856c) {
        local_1b0 = 0.0;
      }
      else {
        OID__Helper_0055dcb0();
        local_1b0 = (float)extraout_ST0;
      }
    }
    else {
      local_1b0 = *(float *)(*(int *)((int)this + 8) + 0xe8);
    }
    OID__Helper_0050a0e0(this,&local_17c,(int)param_1,unaff_EDI);
    OID__Helper_0044a850(this,(int)&local_19c,unaff_EDI);
    Vec3__SetXYZ();
    fVar15 = (float10)fpatan((float10)local_16c,(float10)local_168);
    fVar1 = (float)-fVar15;
    dVar16 = SQRT__Wrapper_004026b0(&local_16c);
    if ((float)dVar16 <= _DAT_005d856c) {
      local_1b4 = 0.0;
    }
    else {
      OID__Helper_0055dcb0();
      local_1b4 = (float)extraout_ST0_00;
    }
    if ((_DAT_005d85c8 <= fVar1) || ((float)pvVar12 < _DAT_005d85e4)) {
      pvVar9 = pvVar12;
      if ((_DAT_005d85e4 <= fVar1) && ((float)pvVar12 < _DAT_005d85c8)) {
        pvVar9 = (void *)((float)pvVar12 + _DAT_005d85e0);
      }
    }
    else {
      pvVar9 = (void *)((float)pvVar12 - _DAT_005d85e0);
    }
    fVar1 = fVar1 - (float)pvVar9;
    if (_DAT_005d85dc <= fVar1) {
      if (_DAT_005d85e8 <= fVar1) {
        fVar1 = fVar1 - _DAT_005d85e0;
      }
    }
    else {
      fVar1 = fVar1 + _DAT_005d85e0;
    }
    if (ABS(fVar1) < *(float *)(*(int *)((int)this + 0xa0) + 0x84)) {
      iVar11 = CEngine__Helper_0040d0f0(*(int *)(*(int *)((int)this + 0xa0) + 0x18));
      if (iVar11 == 0) {
        iVar11 = *(int *)((int)this + 0xa0);
        if (*(int *)(*(int *)(iVar11 + 0x18) + 0x6c) == 0) {
          if (*(int *)((int)this + 0x98) == 0) {
            if (*(float *)(iVar11 + 0x7c) <= local_1b4 - local_1b0) {
              ExceptionList = local_c;
              return 0;
            }
            if (local_1b4 - local_1b0 <= *(float *)(iVar11 + 0x80)) {
              ExceptionList = local_c;
              return 0;
            }
          }
          else {
            if ((_DAT_005d85c8 <= local_1b4) || (local_1b0 < _DAT_005d85e4)) {
              if ((_DAT_005d85e4 <= local_1b4) && (local_1b0 < _DAT_005d85c8)) {
                local_1b0 = local_1b0 + _DAT_005d85e0;
              }
            }
            else {
              local_1b0 = local_1b0 - _DAT_005d85e0;
            }
            local_1b4 = local_1b4 - local_1b0;
            if (_DAT_005d85dc <= local_1b4) {
              if (_DAT_005d85e8 <= local_1b4) {
                local_1b4 = local_1b4 - _DAT_005d85e0;
              }
            }
            else {
              local_1b4 = local_1b4 + _DAT_005d85e0;
            }
            if (*(float *)(iVar11 + 0x84) < ABS(local_1b4)) {
              ExceptionList = local_c;
              return 0;
            }
          }
          if (param_2 == 0) {
            ExceptionList = local_c;
            return 1;
          }
          OID__Helper_0044a850(this,(int)local_3c,unaff_EDI);
          local_d4 = 0;
          local_d0 = 0;
          local_cc = 0;
          local_c4 = *extraout_EAX_06;
          local_c0 = extraout_EAX_06[1];
          local_bc = extraout_EAX_06[2];
          local_b8 = extraout_EAX_06[3];
          local_b4 = local_17c;
          local_b0 = local_178;
          local_ac = local_174;
          local_a8 = local_170;
          local_d8 = &PTR_VFuncSlot_00_00426340_005d8bfc;
          local_4 = 3;
          local_15c[0] = 0;
          local_15c[1] = 0xffffffff;
          local_15c[2] = 0;
          local_15c[3] = 0xbf800000;
          CGeneralVolume__ctor_like_004098e0(&stack0xfffffddc,&local_d8,in_stack_fffffddc);
          iVar11 = OID__Helper_0050b030();
          if ((((iVar11 == 3) && (local_15c[0] != 0)) &&
              ((*(byte *)(local_15c[0] + 0x34) & 0x10) != 0)) &&
             (*(int *)(local_15c[0] + 0x138) == *(int *)((int)param_1 + 0x138))) {
            ExceptionList = local_c;
            return 1;
          }
        }
        else {
          dVar16 = CStaticShadows__Helper_0047eb80
                             (0x6fadc8,(void *)(*(int *)((int)this + 8) + 0x1c));
          if ((double)DAT_006fbdfc < dVar16) {
            ExceptionList = local_c;
            return 1;
          }
        }
      }
      else {
        iVar11 = *(int *)((int)this + 8);
        fVar1 = local_174 - *(float *)(iVar11 + 0x24);
        iVar5 = *(int *)(*(int *)((int)this + 0xa0) + 0x18);
        fVar4 = *(float *)(iVar5 + 0x2c) * _DAT_005d8584;
        fVar10 = *(float *)(iVar5 + 0x3c) * _DAT_005d8c6c;
        fVar6 = SQRT(local_16c * local_16c + local_168 * local_168);
        if (*(int *)((int)this + 0x98) == 0) {
          pvVar12 = (void *)(iVar11 + 0x3c);
          puVar17 = local_118;
          OID__Helper_0040d1f0(&local_14c,*(void **)(iVar11 + 0xe0),0.0,0.0,(float)puVar17);
          CMCBuggy__Helper_0040d320(this_01,puVar17,pvVar12,unaff_EDI);
          Vec3__SetXYZ();
          dVar16 = SQRT__Wrapper_004026b0(&local_19c);
          if ((float)dVar16 <= _DAT_005d856c) {
            fVar15 = (float10)_DAT_005d856c;
          }
          else {
            OID__Helper_0055dcb0();
            fVar15 = extraout_ST0_01;
          }
          fVar2 = (float)(fVar15 + (float10)*(float *)(*(int *)((int)this + 0xa0) + 0x7c));
          fVar3 = (float)(fVar15 + (float10)*(float *)(*(int *)((int)this + 0xa0) + 0x80));
          if (((_DAT_005d8dec < fVar2) && (_DAT_005d8dec < fVar3)) ||
             ((fVar2 < _DAT_005d8dec && (fVar3 < _DAT_005d8dec)))) {
            fVar15 = (float10)fsin((float10)fVar2);
            fVar7 = fVar10 * fVar1 + fVar10 * fVar1;
            fVar13 = (float10)fcos((float10)fVar2);
            fVar1 = (float)((fVar13 * (SQRT(fVar15 * fVar15 * (float10)fVar4 * (float10)fVar4 -
                                            (float10)fVar7) - fVar15 * (float10)fVar4) *
                            (float10)fVar4) / (float10)fVar10);
            fVar15 = (float10)fsin((float10)fVar3);
            fVar13 = (float10)fcos((float10)fVar3);
            fVar15 = (((float10)(float)SQRT(fVar15 * fVar15 * (float10)fVar4 * (float10)fVar4 -
                                            (float10)fVar7) - fVar15 * (float10)fVar4) * fVar13 *
                     (float10)fVar4) / (float10)fVar10;
            local_1ac = fVar1;
            if (fVar15 < (float10)fVar1) {
              local_1ac = (float)fVar15;
              fVar15 = (float10)fVar1;
            }
          }
          else {
            fVar15 = (float10)fsin((float10)fVar2);
            fVar7 = fVar10 * fVar1 + fVar10 * fVar1;
            fVar13 = (float10)fcos((float10)fVar2);
            fVar15 = (fVar13 * (SQRT(fVar15 * fVar15 * (float10)fVar4 * (float10)fVar4 -
                                     (float10)fVar7) - fVar15 * (float10)fVar4) * (float10)fVar4) /
                     (float10)fVar10;
            fVar13 = (float10)fsin((float10)fVar3);
            fVar14 = (float10)fcos((float10)fVar3);
            fVar1 = (float)((fVar14 * (SQRT(fVar13 * fVar13 * (float10)fVar4 * (float10)fVar4 -
                                            (float10)fVar7) - fVar13 * (float10)fVar4) *
                            (float10)fVar4) / (float10)fVar10);
            fVar13 = (float10)fsin((float10)_DAT_005dfca8);
            fVar14 = (float10)fcos((float10)_DAT_005dfca8);
            fVar4 = (float)((((float10)(float)SQRT(fVar13 * fVar13 * (float10)fVar4 * (float10)fVar4
                                                   - (float10)fVar7) - fVar13 * (float10)fVar4) *
                             fVar14 * (float10)fVar4) / (float10)fVar10);
            local_1ac = (float)fVar15;
            if ((float10)fVar1 < fVar15) {
              local_1ac = fVar1;
            }
            if (fVar4 < local_1ac) {
              local_1ac = fVar4;
            }
            if ((float)fVar15 < fVar1) {
              fVar15 = (float10)fVar1;
            }
            if (fVar15 < (float10)fVar4) {
              fVar15 = (float10)fVar4;
            }
          }
          if (((float10)fVar6 <= fVar15) && (local_1ac <= fVar6)) {
            iVar11 = *(int *)((int)this + 8);
            pvVar12 = *(void **)(iVar11 + 0x114);
            local_188 = *(float *)(iVar11 + 0x118);
            local_184 = *(float *)(iVar11 + 0x11c);
            CSquadNormal__Helper_004062d0(local_118,pvVar12,fVar2,0.0,(float)unaff_EDI);
            CSquadNormal__Helper_004062d0(&local_14c,pvVar12,fVar3,0.0,(float)unaff_EDI);
            fVar1 = local_f4 * _DAT_005d8cc0;
            fVar6 = local_104 * _DAT_005d8cc0;
            fVar4 = local_114 * _DAT_005d8cc0;
            OID__Helper_0044a850(this,(int)local_1c,unaff_EDI);
            local_194 = fVar1 + extraout_EAX_02[2];
            local_198 = fVar6 + extraout_EAX_02[1];
            local_19c = fVar4 + *extraout_EAX_02;
            OID__Helper_0044a850(this,(int)local_2c,unaff_EDI);
            Vec3__SetXYZ();
            local_5c = *extraout_EAX_03;
            local_58 = extraout_EAX_03[1];
            local_54 = extraout_EAX_03[2];
            local_50 = extraout_EAX_03[3];
            local_4c = local_19c;
            local_48 = local_198;
            local_44 = local_194;
            local_40 = local_190;
            local_70[0] = &PTR_VFuncSlot_00_00426340_005d8bfc;
            fVar1 = local_128 * _DAT_005d8cc0;
            local_4 = 1;
            fVar6 = local_138 * _DAT_005d8cc0;
            fVar4 = local_148 * _DAT_005d8cc0;
            OID__Helper_0044a850(this,(int)local_15c,unaff_EDI);
            local_194 = fVar1 + extraout_EAX_04[2];
            local_198 = fVar6 + extraout_EAX_04[1];
            local_19c = fVar4 + *extraout_EAX_04;
            OID__Helper_0044a850(this,(int)local_3c,unaff_EDI);
            Vec3__SetXYZ();
            local_90 = *extraout_EAX_05;
            local_8c = extraout_EAX_05[1];
            local_88 = extraout_EAX_05[2];
            local_84 = extraout_EAX_05[3];
            local_80 = local_19c;
            local_7c = local_198;
            local_78 = local_194;
            local_74 = local_190;
            local_a4[0] = &PTR_VFuncSlot_00_00426340_005d8bfc;
            bVar8 = true;
            local_18c = 0.0;
            local_184 = 0.0;
            local_4 = CONCAT31(local_4._1_3_,2);
            local_188 = -NAN;
            local_180 = 0xbf800000;
            CGeneralVolume__ctor_like_004098e0(&stack0xfffffddc,local_70,in_stack_fffffddc);
            iVar11 = OID__Helper_0050b030();
            if ((iVar11 == 1) || (iVar11 == 2)) {
              bVar8 = false;
            }
            if ((((iVar11 == 3) && (local_18c != 0.0)) &&
                ((*(byte *)((int)local_18c + 0x34) & 0x10) != 0)) &&
               (*(int *)((int)local_18c + 0x138) != *(int *)((int)param_1 + 0x138))) {
              bVar8 = false;
            }
            CGeneralVolume__ctor_like_004098e0(&stack0xfffffddc,local_a4,in_stack_fffffddc);
            iVar11 = OID__Helper_0050b030();
            if ((iVar11 == 1) || (iVar11 == 2)) {
              bVar8 = false;
            }
            if ((((iVar11 != 3) || (local_18c == 0.0)) ||
                (((*(byte *)((int)local_18c + 0x34) & 0x10) == 0 ||
                 (*(int *)((int)local_18c + 0x138) == *(int *)((int)param_1 + 0x138))))) && (bVar8))
            {
              ExceptionList = local_c;
              return 1;
            }
          }
        }
        else {
          fVar15 = (float10)fcos((float10)local_1b0);
          fVar13 = (float10)fsin((float10)local_1b0);
          fVar13 = fVar13 * (float10)fVar4;
          fVar15 = ((SQRT((float10)fVar10 * (float10)fVar1 + (float10)fVar10 * (float10)fVar1 +
                          fVar13 * fVar13) - fVar13) / (float10)fVar10) * fVar15 * (float10)fVar4;
          if (fVar15 < (float10)_DAT_005d856c) {
            fVar15 = (float10)_DAT_005d856c;
          }
          if (ABS((float10)fVar6 - fVar15) < (float10)_DAT_005db4e8) {
            CSquadNormal__Helper_004062d0(local_118,pvVar12,local_1b0,0.0,(float)unaff_EDI);
            fVar1 = local_f4 * _DAT_005d8cc0;
            fVar6 = local_104 * _DAT_005d8cc0;
            fVar4 = local_114 * _DAT_005d8cc0;
            OID__Helper_0044a850(this,(int)local_2c,unaff_EDI);
            local_184 = fVar1 + extraout_EAX_00[2];
            local_188 = fVar6 + extraout_EAX_00[1];
            local_18c = fVar4 + *extraout_EAX_00;
            OID__Helper_0044a850(this,(int)local_1c,unaff_EDI);
            Vec3__SetXYZ();
            local_138 = (float)*extraout_EAX_01;
            local_134 = extraout_EAX_01[1];
            local_130 = extraout_EAX_01[2];
            local_12c = extraout_EAX_01[3];
            local_128 = local_18c;
            local_124 = local_188;
            local_120 = local_184;
            local_11c = local_180;
            local_14c = &PTR_VFuncSlot_00_00426340_005d8bfc;
            local_4 = 0;
            local_19c = 0.0;
            local_198 = -NAN;
            local_194 = 0.0;
            local_190 = 0xbf800000;
            CGeneralVolume__ctor_like_004098e0(&stack0xfffffddc,&local_14c,in_stack_fffffddc);
            iVar11 = OID__Helper_0050b030();
            if (iVar11 == 0) {
              ExceptionList = local_c;
              return 1;
            }
            if (iVar11 == 3) {
              ExceptionList = local_c;
              return 1;
            }
          }
        }
      }
    }
  }
  ExceptionList = local_c;
  return 0;
}
