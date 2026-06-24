/* address: 0x0057f391 */
/* name: CDXTexture__ResampleVolumeTrilinear */
/* signature: int __fastcall CDXTexture__ResampleVolumeTrilinear(void * param_1) */


int __fastcall CDXTexture__ResampleVolumeTrilinear(void *param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  float fVar25;
  float fVar26;
  float fVar27;
  float fVar28;
  float fVar29;
  float fVar30;
  float fVar31;
  float fVar32;
  float fVar33;
  float fVar34;
  float fVar35;
  float fVar36;
  float fVar37;
  float fVar38;
  uint uVar39;
  void *pvVar40;
  void *ptr;
  void *ptr_00;
  void *ptr_01;
  float *extraout_EAX;
  void *extraout_EAX_00;
  int *piVar41;
  int iVar42;
  float *pfVar43;
  float *pfVar44;
  float *pfVar45;
  float *pfVar46;
  float *pfVar47;
  float *pfVar48;
  void *pvVar49;
  void *pvVar50;
  float *pfVar51;
  int iVar52;
  float *pfVar53;
  int *piVar54;
  float *local_48;
  uint local_3c;
  void *local_38;
  uint local_30;
  void *local_2c;
  uint local_28;
  void *local_24;
  void *local_20;
  void *local_1c;
  int local_18;
  float *local_14;
  int local_10;
  undefined4 *local_c;

  local_14 = (float *)0x0;
  local_2c = (void *)0x0;
  uVar39 = *(uint *)((int)param_1 + 8);
  if ((char)uVar39 != '\x03') {
    return -0x7fffbffb;
  }
  CFastVB__BuildResampleKernel1D(~(uVar39 >> 0x10) & 1);
  CFastVB__BuildResampleKernel1D(~(uVar39 >> 0x11) & 1);
  CFastVB__BuildResampleKernel1D(~(uVar39 >> 0x12) & 1);
  if (((ptr != (void *)0x0) && (ptr_00 != (void *)0x0)) && (ptr_01 != (void *)0x0)) {
    iVar42 = *(int *)(*(int *)((int)param_1 + 4) + 0x1060);
    OID__AllocObject_DefaultTag_00662b2c(iVar42 << 4);
    if (extraout_EAX == (float *)0x0) {
      local_14 = (float *)0x0;
    }
    else {
      _vector_constructor_iterator_(extraout_EAX,0x10,iVar42,CFastVB__ReturnInputInt);
      local_14 = extraout_EAX;
    }
    if (local_14 != (float *)0x0) {
      iVar42 = *(int *)(*(int *)param_1 + 0x1060);
      OID__AllocObject_DefaultTag_00662b2c(iVar42 << 6);
      if (extraout_EAX_00 == (void *)0x0) {
        local_2c = (void *)0x0;
      }
      else {
        _vector_constructor_iterator_(extraout_EAX_00,0x10,iVar42 << 2,CFastVB__ReturnInputInt);
        local_2c = extraout_EAX_00;
      }
      if (local_2c != (void *)0x0) {
        iVar42 = *(int *)(*(int *)param_1 + 0x1060);
        local_30 = 0;
        local_20 = (void *)(iVar42 * 0x10 + (int)local_2c);
        local_24 = (void *)(iVar42 * 0x20 + (int)local_2c);
        iVar52 = *(int *)((int)param_1 + 4);
        pvVar49 = (void *)(iVar42 * 0x30 + (int)local_2c);
        local_38 = local_2c;
        if (*(int *)(iVar52 + 0x1068) != 0) {
          local_c = (undefined4 *)((int)ptr_01 + 8);
          local_1c = pvVar49;
          do {
            local_28 = 0;
            local_18 = -1;
            local_10 = -1;
            if (*(int *)(iVar52 + 0x1064) != 0) {
              piVar54 = (int *)((int)ptr_00 + 8);
              do {
                iVar52 = local_10;
                pvVar40 = local_20;
                iVar42 = piVar54[-2];
                local_3c = 0;
                pvVar50 = pvVar49;
                if (iVar42 != local_18) {
                  if (iVar42 == local_10) {
                    local_10 = -1;
                    local_18 = iVar52;
                    local_20 = local_38;
                    local_38 = pvVar40;
                    local_1c = local_24;
                    pvVar50 = local_24;
                    local_24 = pvVar49;
                  }
                  else {
                    (**(code **)(**(int **)param_1 + 4))(iVar42,local_c[-2],local_38);
                    (**(code **)(**(int **)param_1 + 4))(iVar42,*local_c,local_24);
                    local_18 = iVar42;
                  }
                }
                iVar42 = *piVar54;
                if (iVar42 != local_10) {
                  (**(code **)(**(int **)param_1 + 4))(iVar42,local_c[-2],local_20);
                  (**(code **)(**(int **)param_1 + 4))(iVar42,*local_c,pvVar50);
                  local_10 = iVar42;
                }
                pvVar49 = pvVar50;
                if (*(int *)(*(int *)((int)param_1 + 4) + 0x1060) != 0) {
                  piVar41 = (int *)((int)ptr + 8);
                  local_48 = local_14;
                  do {
                    fVar1 = (float)piVar41[1];
                    iVar42 = *piVar41 * 0x10;
                    pfVar51 = (float *)((int)pvVar50 + iVar42);
                    fVar2 = pfVar51[1];
                    fVar3 = pfVar51[2];
                    fVar4 = pfVar51[3];
                    fVar5 = (float)piVar41[-1];
                    iVar52 = piVar41[-2] * 0x10;
                    pfVar44 = (float *)((int)local_1c + iVar52);
                    fVar6 = pfVar44[1];
                    fVar7 = pfVar44[2];
                    fVar8 = pfVar44[3];
                    pfVar45 = (float *)((int)local_24 + iVar42);
                    fVar9 = (float)piVar54[1];
                    fVar10 = (float)piVar41[1];
                    fVar11 = pfVar45[1];
                    fVar12 = pfVar45[2];
                    fVar13 = pfVar45[3];
                    fVar14 = (float)piVar41[-1];
                    pfVar46 = (float *)((int)local_24 + iVar52);
                    fVar15 = pfVar46[1];
                    fVar16 = pfVar46[2];
                    fVar17 = pfVar46[3];
                    fVar18 = (float)piVar54[-1];
                    fVar19 = (float)local_c[1];
                    pfVar47 = (float *)((int)local_20 + iVar42);
                    fVar20 = (float)piVar41[1];
                    fVar21 = pfVar47[1];
                    fVar22 = pfVar47[2];
                    fVar23 = pfVar47[3];
                    fVar24 = (float)piVar41[-1];
                    pfVar48 = (float *)((int)local_20 + iVar52);
                    fVar25 = pfVar48[1];
                    fVar26 = pfVar48[2];
                    fVar27 = pfVar48[3];
                    pfVar43 = (float *)(iVar42 + (int)local_38);
                    fVar28 = (float)piVar54[1];
                    fVar29 = (float)piVar41[1];
                    fVar30 = pfVar43[1];
                    fVar31 = pfVar43[2];
                    pfVar53 = (float *)(iVar52 + (int)local_38);
                    fVar32 = pfVar43[3];
                    fVar33 = (float)piVar41[-1];
                    fVar34 = pfVar53[1];
                    fVar35 = pfVar53[2];
                    fVar36 = pfVar53[3];
                    fVar37 = (float)piVar54[-1];
                    fVar38 = (float)local_c[-1];
                    piVar41 = piVar41 + 4;
                    local_3c = local_3c + 1;
                    *local_48 = ((fVar33 * *pfVar53 + fVar29 * *pfVar43) * fVar37 +
                                (fVar24 * *pfVar48 + fVar20 * *pfVar47) * fVar28) * fVar38 +
                                ((fVar14 * *pfVar46 + fVar10 * *pfVar45) * fVar18 +
                                (fVar5 * *pfVar44 + fVar1 * *pfVar51) * fVar9) * fVar19;
                    local_48[1] = ((fVar33 * fVar34 + fVar29 * fVar30) * fVar37 +
                                  (fVar24 * fVar25 + fVar20 * fVar21) * fVar28) * fVar38 +
                                  ((fVar14 * fVar15 + fVar10 * fVar11) * fVar18 +
                                  (fVar5 * fVar6 + fVar1 * fVar2) * fVar9) * fVar19;
                    local_48[2] = ((fVar33 * fVar35 + fVar29 * fVar31) * fVar37 +
                                  (fVar24 * fVar26 + fVar20 * fVar22) * fVar28) * fVar38 +
                                  ((fVar14 * fVar16 + fVar10 * fVar12) * fVar18 +
                                  (fVar5 * fVar7 + fVar1 * fVar3) * fVar9) * fVar19;
                    local_48[3] = ((fVar33 * fVar36 + fVar29 * fVar32) * fVar37 +
                                  (fVar24 * fVar27 + fVar20 * fVar23) * fVar28) * fVar38 +
                                  ((fVar14 * fVar17 + fVar10 * fVar13) * fVar18 +
                                  (fVar5 * fVar8 + fVar1 * fVar4) * fVar9) * fVar19;
                    pvVar49 = local_1c;
                    pvVar50 = local_1c;
                    local_48 = local_48 + 4;
                  } while (local_3c < *(uint *)(*(int *)((int)param_1 + 4) + 0x1060));
                }
                (**(code **)(**(int **)((int)param_1 + 4) + 8))(local_28,local_30,local_14);
                piVar54 = piVar54 + 4;
                local_28 = local_28 + 1;
              } while (local_28 < *(uint *)(*(int *)((int)param_1 + 4) + 0x1064));
            }
            local_c = local_c + 4;
            local_30 = local_30 + 1;
            iVar52 = *(int *)((int)param_1 + 4);
          } while (local_30 < *(uint *)(iVar52 + 0x1068));
        }
        iVar42 = 0;
        goto LAB_0057f9db;
      }
    }
  }
  iVar42 = -0x7ff8fff2;
LAB_0057f9db:
  OID__FreeObject_Callback(ptr);
  OID__FreeObject_Callback(ptr_00);
  OID__FreeObject_Callback(ptr_01);
  OID__FreeObject_Callback(local_14);
  OID__FreeObject_Callback(local_2c);
  return iVar42;
}
