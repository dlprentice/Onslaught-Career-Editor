/* address: 0x00509140 */
/* name: OID__UpdateAimTransformAndAttachTargetReader */
/* signature: void __thiscall OID__UpdateAimTransformAndAttachTargetReader(void * this, void * param_1, void * param_2, void * param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
OID__UpdateAimTransformAndAttachTargetReader(void *this,void *param_1,void *param_2,void *param_3)

{
  int iVar1;
  float10 fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  int iVar6;
  int extraout_EAX;
  undefined4 *extraout_EAX_00;
  undefined4 *puVar7;
  void *unaff_EDI;
  undefined4 *puVar8;
  float10 fVar9;
  float10 extraout_ST0;
  float10 extraout_ST0_00;
  float10 fVar10;
  float10 fVar11;
  float10 fVar12;
  float10 fVar13;
  float10 extraout_ST0_01;
  double dVar14;
  float local_7c;
  float local_74;
  float local_68;
  float local_60;
  float local_5c;
  float local_58;
  undefined1 local_50 [16];
  undefined1 local_40 [4];
  undefined4 local_3c;
  undefined4 local_30 [12];

  OID__Helper_0044a850(this,(int)local_40,unaff_EDI);
  Vec3__SetXYZ();
  if (*(int *)(*(int *)((int)this + 0xa4) + 0x28) == 0) {
    OID__Helper_0044a930(this,(int)local_30,unaff_EDI);
    puVar8 = (undefined4 *)((int)this + 0x30);
    iVar6 = 0xc;
    puVar7 = extraout_EAX_00;
  }
  else {
    iVar6 = CEngine__Helper_0040d0f0(*(int *)(*(int *)((int)this + 0xa0) + 0x18));
    if (iVar6 == 0) {
      if (SQRT(local_58 * local_58 + local_60 * local_60 + local_5c * local_5c) <= _DAT_005d856c) {
        local_68 = 0.0;
      }
      else {
        OID__Helper_0055dcb0();
        local_68 = (float)extraout_ST0_01;
      }
      fVar9 = (float10)fpatan((float10)local_60,(float10)local_5c);
      CSquadNormal__Helper_004062d0(local_30,(void *)(float)-fVar9,local_68,0.0,(float)unaff_EDI);
      puVar8 = (undefined4 *)((int)this + 0x30);
      iVar6 = 0xc;
      puVar7 = local_30;
    }
    else {
      local_3c = *(undefined4 *)(*(int *)(*(int *)((int)this + 0xa0) + 0x18) + 0x2c);
      OID__Helper_0044a930(this,(int)local_30,unaff_EDI);
      Vec3__SetXYZ();
      OID__Helper_0044a850(this,(int)local_40,unaff_EDI);
      local_68 = *(float *)((int)param_2 + 8) - *(float *)(extraout_EAX + 8);
      iVar6 = *(int *)((int)this + 0xa0);
      fVar4 = *(float *)(*(int *)(iVar6 + 0x18) + 0x2c) * _DAT_005d8584;
      fVar5 = *(float *)(*(int *)(iVar6 + 0x18) + 0x3c) * _DAT_005d8c6c;
      fVar3 = SQRT(local_60 * local_60 + local_5c * local_5c);
      if (*(int *)((int)this + 0x98) == 0) {
        dVar14 = SQRT__Wrapper_004026b0(local_50);
        if (dVar14 <= (double)_DAT_005d856c) {
          fVar9 = (float10)_DAT_005d856c;
        }
        else {
          OID__Helper_0055dcb0();
          fVar9 = extraout_ST0;
        }
        iVar1 = *(int *)((int)this + 0xa0);
        local_74 = (float)(fVar9 + (float10)*(float *)(iVar6 + 0x7c));
        dVar14 = SQRT__Wrapper_004026b0(local_50);
        if (dVar14 <= (double)_DAT_005d856c) {
          fVar9 = (float10)_DAT_005d856c;
        }
        else {
          OID__Helper_0055dcb0();
          fVar9 = extraout_ST0_00;
        }
        fVar9 = fVar9 + (float10)*(float *)(iVar1 + 0x80);
      }
      else {
        local_74 = *(float *)(iVar6 + 0x7c);
        fVar9 = (float10)*(float *)(iVar6 + 0x80);
      }
      local_7c = 9999999.0;
      if (fVar9 < (float10)local_74) {
        fVar2 = (float10)local_68;
        fVar9 = (float10)(float)fVar9;
        do {
          fVar10 = (float10)fcos(fVar9);
          fVar10 = fVar10 * (float10)fVar4;
          fVar11 = (float10)fsin(fVar9);
          fVar11 = fVar11 * (float10)fVar4;
          fVar12 = SQRT(fVar11 * fVar11 + (float10)fVar5 * fVar2 + (float10)fVar5 * fVar2);
          fVar13 = ((fVar12 - fVar11) / (float10)fVar5) * fVar10;
          if (((float10)_DAT_005d856c < fVar13) &&
             (fVar13 = ABS(fVar13 - (float10)fVar3), fVar13 < (float10)local_7c)) {
            local_7c = (float)fVar13;
            local_68 = (float)fVar9;
          }
          fVar10 = ((-fVar11 - fVar12) / (float10)fVar5) * fVar10;
          if (((float10)_DAT_005d856c < fVar10) &&
             (fVar10 = ABS(fVar10 - (float10)fVar3), fVar10 < (float10)local_7c)) {
            local_7c = (float)fVar10;
            local_68 = (float)fVar9;
          }
          fVar9 = fVar9 + (float10)_DAT_005d8cb8;
        } while (fVar9 < (float10)local_74);
      }
      fVar9 = (float10)fpatan((float10)local_60,(float10)local_5c);
      CSquadNormal__Helper_004062d0(local_30,(void *)(float)-fVar9,local_68,0.0,(float)unaff_EDI);
      iVar6 = 0xc;
      puVar7 = local_30;
      puVar8 = (undefined4 *)((int)this + 0x30);
    }
  }
  for (; iVar6 != 0; iVar6 = iVar6 + -1) {
    *puVar8 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar8 = puVar8 + 1;
  }
  *(undefined4 *)((int)this + 0x80) = 1;
  *(undefined4 *)((int)this + 0x84) = *(undefined4 *)param_2;
  *(undefined4 *)((int)this + 0x88) = *(undefined4 *)((int)param_2 + 4);
  *(undefined4 *)((int)this + 0x8c) = *(undefined4 *)((int)param_2 + 8);
  *(undefined4 *)((int)this + 0x90) = *(undefined4 *)((int)param_2 + 0xc);
  CGenericActiveReader__SetReader((void *)((int)this + 0x2c),param_1);
  return;
}
