/* address: 0x0057eadb */
/* name: CDXTexture__DownsampleVolume2x2x2 */
/* signature: int __fastcall CDXTexture__DownsampleVolume2x2x2(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CDXTexture__DownsampleVolume2x2x2(void *param_1)

{
  int *piVar1;
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
  float fVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  float fVar25;
  float fVar26;
  uint uVar27;
  int iVar28;
  float fVar29;
  int iVar30;
  float *extraout_EAX;
  void *extraout_EAX_00;
  void *extraout_EAX_01;
  void *pvVar31;
  void *pvVar32;
  float *pfVar33;
  float *pfVar34;
  float *pfVar35;
  float *pfVar36;
  float *pfVar37;
  float *pfVar38;
  void *pvVar39;
  float *pfVar40;
  void *pvVar41;
  void *local_34;
  void *local_30;
  float *local_2c;
  uint local_20;
  void *local_1c;
  uint local_18;
  float *local_14;
  uint local_c;
  void *local_8;

  if (*(char *)((int)param_1 + 8) == '\x05') {
    iVar30 = *(int *)param_1;
    uVar27 = *(uint *)(iVar30 + 0x1060);
    iVar28 = *(int *)((int)param_1 + 4);
    if ((((*(uint *)(iVar28 + 0x1060) == uVar27 >> 1) ||
         ((*(uint *)(iVar28 + 0x1060) == 1 && (uVar27 == 1)))) &&
        ((*(uint *)(iVar28 + 0x1064) == *(uint *)(iVar30 + 0x1064) >> 1 ||
         ((*(uint *)(iVar28 + 0x1064) == 1 && (*(int *)(iVar30 + 0x1064) == 1)))))) &&
       (*(uint *)(iVar28 + 0x1068) == *(uint *)(iVar30 + 0x1068) >> 1)) {
      if ((1 < uVar27) && ((uVar27 & 1) != 0)) {
        *(uint *)(iVar30 + 0x1060) = uVar27 & 0xfffffffe;
        piVar1 = (int *)(*(int *)param_1 + 0x106c);
        *piVar1 = *piVar1 - *(int *)(*(int *)param_1 + 0x1070);
      }
      uVar27 = *(uint *)(*(int *)param_1 + 0x1064);
      if (1 < uVar27) {
        *(uint *)(*(int *)param_1 + 0x1064) = uVar27 & 0xfffffffe;
      }
      uVar27 = *(uint *)(*(int *)param_1 + 0x1068);
      if (1 < uVar27) {
        *(uint *)(*(int *)param_1 + 0x1068) = uVar27 & 0xfffffffe;
      }
      iVar30 = *(int *)(*(int *)((int)param_1 + 4) + 0x1060);
      OID__AllocObject_DefaultTag_00662b2c(iVar30 << 4);
      if (extraout_EAX == (float *)0x0) {
        local_14 = (float *)0x0;
      }
      else {
        _vector_constructor_iterator_(extraout_EAX,0x10,iVar30,CFastVB__ReturnInputInt);
        local_14 = extraout_EAX;
      }
      if (local_14 == (float *)0x0) {
        iVar30 = -0x7ff8fff2;
      }
      else {
        iVar30 = *(int *)(*(int *)param_1 + 0x1060);
        if (*(int *)(*(int *)param_1 + 0x1064) == 1) {
          OID__AllocObject_DefaultTag_00662b2c(iVar30 << 5);
          if (extraout_EAX_00 == (void *)0x0) {
            local_8 = (void *)0x0;
          }
          else {
            _vector_constructor_iterator_(extraout_EAX_00,0x10,iVar30 << 1,CFastVB__ReturnInputInt);
            local_8 = extraout_EAX_00;
          }
          iVar30 = *(int *)(*(int *)param_1 + 0x1060);
          pvVar41 = (void *)(iVar30 * 0x10 + (int)local_8);
          local_1c = local_8;
          pvVar31 = pvVar41;
        }
        else {
          OID__AllocObject_DefaultTag_00662b2c(iVar30 << 6);
          if (extraout_EAX_01 == (void *)0x0) {
            local_8 = (void *)0x0;
          }
          else {
            _vector_constructor_iterator_(extraout_EAX_01,0x10,iVar30 << 2,CFastVB__ReturnInputInt);
            local_8 = extraout_EAX_01;
          }
          iVar30 = *(int *)(*(int *)param_1 + 0x1060);
          pvVar31 = (void *)(iVar30 * 0x10 + (int)local_8);
          local_1c = (void *)(iVar30 * 0x20 + (int)local_8);
          pvVar41 = (void *)(iVar30 * 0x30 + (int)local_8);
        }
        if (local_8 == (void *)0x0) {
          iVar30 = -0x7ff8fff2;
        }
        else {
          if (iVar30 == 1) {
            local_34 = local_8;
            pvVar32 = local_1c;
            pvVar39 = pvVar41;
            local_30 = pvVar31;
          }
          else {
            local_34 = (void *)((int)local_8 + 0x10);
            local_30 = (void *)((int)pvVar31 + 0x10);
            pvVar32 = (void *)((int)local_1c + 0x10);
            pvVar39 = (void *)((int)pvVar41 + 0x10);
          }
          local_18 = 0;
          iVar30 = *(int *)((int)param_1 + 4);
          if (*(int *)(iVar30 + 0x1068) != 0) {
            do {
              local_c = 0;
              if (*(int *)(iVar30 + 0x1064) != 0) {
                do {
                  iVar30 = local_18 * 2;
                  (**(code **)(**(int **)param_1 + 4))(local_c * 2,iVar30,local_8);
                  if (pvVar31 != local_8) {
                    (**(code **)(**(int **)param_1 + 4))(local_c * 2,iVar30 + 1,pvVar31);
                  }
                  if (local_1c != local_8) {
                    (**(code **)(**(int **)param_1 + 4))(local_c * 2 + 1,iVar30,local_1c);
                  }
                  if ((pvVar41 != pvVar31) && (pvVar41 != local_1c)) {
                    (**(code **)(**(int **)param_1 + 4))(local_c * 2 + 1,iVar30 + 1,pvVar41);
                  }
                  fVar29 = _DAT_005e72e8;
                  local_20 = 0;
                  if (*(int *)(*(int *)((int)param_1 + 4) + 0x1060) != 0) {
                    local_2c = local_14;
                    do {
                      iVar30 = local_20 * 0x20;
                      pfVar34 = (float *)((int)local_34 + iVar30);
                      pfVar40 = (float *)((int)local_8 + iVar30);
                      fVar3 = pfVar34[1];
                      fVar4 = pfVar40[1];
                      fVar5 = pfVar34[2];
                      fVar6 = pfVar40[2];
                      fVar7 = pfVar34[3];
                      pfVar2 = (float *)(iVar30 + (int)pvVar31);
                      fVar8 = pfVar40[3];
                      fVar9 = pfVar2[1];
                      fVar10 = pfVar2[2];
                      fVar11 = pfVar2[3];
                      pfVar35 = (float *)((int)local_30 + iVar30);
                      fVar12 = pfVar35[1];
                      fVar13 = pfVar35[2];
                      fVar14 = pfVar35[3];
                      pfVar36 = (float *)((int)local_1c + iVar30);
                      fVar15 = pfVar36[1];
                      fVar16 = pfVar36[2];
                      fVar17 = pfVar36[3];
                      pfVar37 = (float *)((int)pvVar32 + iVar30);
                      fVar18 = pfVar37[1];
                      fVar19 = pfVar37[2];
                      fVar20 = pfVar37[3];
                      pfVar38 = (float *)((int)pvVar41 + iVar30);
                      fVar21 = pfVar38[1];
                      fVar22 = pfVar38[2];
                      fVar23 = pfVar38[3];
                      pfVar33 = (float *)(iVar30 + (int)pvVar39);
                      local_20 = local_20 + 1;
                      fVar24 = pfVar33[1];
                      fVar25 = pfVar33[2];
                      fVar26 = pfVar33[3];
                      *local_2c = (*pfVar34 + *pfVar40 + *pfVar2 + *pfVar35 + *pfVar36 + *pfVar37 +
                                   *pfVar38 + *pfVar33) * fVar29;
                      local_2c[1] = (fVar3 + fVar4 + fVar9 + fVar12 + fVar15 + fVar18 + fVar21 +
                                    fVar24) * fVar29;
                      local_2c[2] = (fVar5 + fVar6 + fVar10 + fVar13 + fVar16 + fVar19 + fVar22 +
                                    fVar25) * fVar29;
                      local_2c[3] = (fVar7 + fVar8 + fVar11 + fVar14 + fVar17 + fVar20 + fVar23 +
                                    fVar26) * fVar29;
                      local_2c = local_2c + 4;
                    } while (local_20 < *(uint *)(*(int *)((int)param_1 + 4) + 0x1060));
                  }
                  (**(code **)(**(int **)((int)param_1 + 4) + 8))(local_c,local_18,local_14);
                  local_c = local_c + 1;
                } while (local_c < *(uint *)(*(int *)((int)param_1 + 4) + 0x1064));
              }
              local_18 = local_18 + 1;
              iVar30 = *(int *)((int)param_1 + 4);
            } while (local_18 < *(uint *)(iVar30 + 0x1068));
          }
          OID__FreeObject_Callback(local_8);
          iVar30 = 0;
        }
        OID__FreeObject_Callback(local_14);
      }
    }
    else {
      iVar30 = -0x7fffbffb;
    }
  }
  else {
    iVar30 = -0x7fffbffb;
  }
  return iVar30;
}
