/* address: 0x0057f002 */
/* name: CDXTexture__ResampleSurfaceBilinear */
/* signature: int __fastcall CDXTexture__ResampleSurfaceBilinear(void * param_1) */


int __fastcall CDXTexture__ResampleSurfaceBilinear(void *param_1)

{
  float *pfVar1;
  float *pfVar2;
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
  uint uVar21;
  int iVar22;
  void *ptr;
  void *ptr_00;
  float *extraout_EAX;
  void *extraout_EAX_00;
  int *piVar23;
  float *pfVar24;
  int *piVar25;
  float *pfVar26;
  int iVar27;
  void *pvVar28;
  void *pvVar29;
  uint local_34;
  int local_30;
  float *local_2c;
  void *local_24;
  uint local_20;
  int local_1c;
  void *local_14;
  void *local_10;
  float *local_c;

  local_c = (float *)0x0;
  local_14 = (void *)0x0;
  uVar21 = *(uint *)((int)param_1 + 8);
  if ((char)uVar21 != '\x03') {
    return -0x7fffbffb;
  }
  if ((*(int *)(*(int *)((int)param_1 + 4) + 0x1068) != 1) ||
     (*(int *)(*(int *)param_1 + 0x1068) != 1)) {
    return -0x7fffbffb;
  }
  CFastVB__BuildResampleKernel1D(~(uVar21 >> 0x10) & 1);
  CFastVB__BuildResampleKernel1D(~(uVar21 >> 0x11) & 1);
  if ((ptr != (void *)0x0) && (ptr_00 != (void *)0x0)) {
    iVar27 = *(int *)(*(int *)((int)param_1 + 4) + 0x1060);
    OID__AllocObject_DefaultTag_00662b2c(iVar27 << 4);
    if (extraout_EAX == (float *)0x0) {
      local_c = (float *)0x0;
    }
    else {
      _vector_constructor_iterator_(extraout_EAX,0x10,iVar27,CFastVB__ReturnInputInt);
      local_c = extraout_EAX;
    }
    if (local_c != (float *)0x0) {
      iVar27 = *(int *)(*(int *)param_1 + 0x1060);
      OID__AllocObject_DefaultTag_00662b2c(iVar27 << 5);
      if (extraout_EAX_00 == (void *)0x0) {
        local_14 = (void *)0x0;
      }
      else {
        _vector_constructor_iterator_(extraout_EAX_00,0x10,iVar27 << 1,CFastVB__ReturnInputInt);
        local_14 = extraout_EAX_00;
      }
      if (local_14 != (void *)0x0) {
        local_20 = 0;
        local_30 = -1;
        local_1c = -1;
        pvVar28 = (void *)(*(int *)(*(int *)param_1 + 0x1060) * 0x10 + (int)local_14);
        local_24 = local_14;
        if (*(int *)(*(int *)((int)param_1 + 4) + 0x1064) != 0) {
          piVar25 = (int *)((int)ptr_00 + 8);
          local_10 = pvVar28;
          do {
            iVar22 = local_1c;
            iVar27 = piVar25[-2];
            local_34 = 0;
            pvVar29 = pvVar28;
            if (iVar27 != local_30) {
              if (iVar27 == local_1c) {
                local_1c = -1;
                local_30 = iVar22;
                local_10 = local_24;
                pvVar29 = local_24;
                local_24 = pvVar28;
              }
              else {
                (**(code **)(**(int **)param_1 + 4))(iVar27,0,local_24);
                local_30 = iVar27;
              }
            }
            iVar27 = *piVar25;
            if (iVar27 != local_1c) {
              (**(code **)(**(int **)param_1 + 4))(iVar27,0,pvVar29);
              local_1c = iVar27;
            }
            pvVar28 = pvVar29;
            if (*(int *)(*(int *)((int)param_1 + 4) + 0x1060) != 0) {
              piVar23 = (int *)((int)ptr + 8);
              local_2c = local_c;
              do {
                fVar3 = (float)piVar23[1];
                pfVar1 = (float *)(*piVar23 * 0x10 + (int)pvVar29);
                fVar4 = pfVar1[1];
                fVar5 = pfVar1[2];
                fVar6 = pfVar1[3];
                fVar7 = (float)piVar23[-1];
                pfVar2 = (float *)(piVar23[-2] * 0x10 + (int)pvVar29);
                pfVar24 = (float *)(*piVar23 * 0x10 + (int)local_24);
                fVar8 = pfVar2[1];
                fVar9 = pfVar2[2];
                fVar10 = pfVar2[3];
                fVar11 = (float)piVar25[1];
                fVar12 = (float)piVar23[1];
                fVar13 = pfVar24[1];
                fVar14 = pfVar24[2];
                pfVar26 = (float *)(piVar23[-2] * 0x10 + (int)local_24);
                fVar15 = pfVar24[3];
                fVar16 = (float)piVar23[-1];
                piVar23 = piVar23 + 4;
                local_34 = local_34 + 1;
                fVar17 = pfVar26[1];
                fVar18 = pfVar26[2];
                fVar19 = pfVar26[3];
                fVar20 = (float)piVar25[-1];
                *local_2c = (fVar16 * *pfVar26 + fVar12 * *pfVar24) * fVar20 +
                            (fVar7 * *pfVar2 + fVar3 * *pfVar1) * fVar11;
                local_2c[1] = (fVar16 * fVar17 + fVar12 * fVar13) * fVar20 +
                              (fVar7 * fVar8 + fVar3 * fVar4) * fVar11;
                local_2c[2] = (fVar16 * fVar18 + fVar12 * fVar14) * fVar20 +
                              (fVar7 * fVar9 + fVar3 * fVar5) * fVar11;
                local_2c[3] = (fVar16 * fVar19 + fVar12 * fVar15) * fVar20 +
                              (fVar7 * fVar10 + fVar3 * fVar6) * fVar11;
                pvVar29 = local_10;
                pvVar28 = local_10;
                local_2c = local_2c + 4;
              } while (local_34 < *(uint *)(*(int *)((int)param_1 + 4) + 0x1060));
            }
            (**(code **)(**(int **)((int)param_1 + 4) + 8))(local_20,0,local_c);
            piVar25 = piVar25 + 4;
            local_20 = local_20 + 1;
          } while (local_20 < *(uint *)(*(int *)((int)param_1 + 4) + 0x1064));
        }
        iVar27 = 0;
        goto LAB_0057f35d;
      }
    }
  }
  iVar27 = -0x7ff8fff2;
LAB_0057f35d:
  OID__FreeObject_Callback(ptr);
  OID__FreeObject_Callback(ptr_00);
  OID__FreeObject_Callback(local_c);
  OID__FreeObject_Callback(local_14);
  return iVar27;
}
