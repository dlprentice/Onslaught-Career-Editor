/* address: 0x005725e0 */
/* name: CFastVB__Helper_005725e0 */
/* signature: void __thiscall CFastVB__Helper_005725e0(void * this, void * param_1, int param_2, int param_3, void * param_4, int param_5) */


void __thiscall
CFastVB__Helper_005725e0(void *this,void *param_1,int param_2,int param_3,void *param_4,int param_5)

{
  int *piVar1;
  undefined4 uVar2;
  void *pvVar3;
  bool bVar4;
  int *extraout_EAX;
  int iVar5;
  undefined4 *extraout_EAX_00;
  undefined4 *extraout_EAX_01;
  undefined4 *extraout_EAX_02;
  undefined4 *extraout_EAX_03;
  undefined4 *extraout_EAX_04;
  undefined4 *extraout_EAX_05;
  undefined4 *extraout_EAX_06;
  undefined4 *extraout_EAX_07;
  int *piVar6;
  int *this_00;
  void *unaff_EDI;
  int iVar7;
  double dVar8;
  char local_dd;
  int local_d8;
  int local_d4;
  int *local_d0;
  int local_cc;
  int local_c8;
  int *local_c4;
  int local_c0;
  void *local_bc;
  undefined4 *local_b8;
  char local_b4;
  char local_b3;
  void *local_b0;
  undefined1 local_ac;
  undefined4 local_a8;
  undefined4 local_a4;
  undefined4 local_a0;
  uint local_9c;
  undefined4 *local_98;
  undefined4 *local_94;
  void *local_90;
  undefined4 *local_8c;
  int local_88;
  double local_84;
  undefined4 *local_7c;
  undefined4 *local_78;
  undefined4 *local_74;
  int local_70;
  uint local_6c;
  undefined4 uStack_68;
  undefined1 local_64 [4];
  undefined1 local_60 [12];
  undefined4 local_54;
  uint local_48;
  undefined4 local_3c;
  uint local_30;
  undefined4 local_24;
  uint local_18;
  undefined1 local_14 [8];
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d7f89;
  local_c = ExceptionList;
  local_88 = (int)param_4 * 6;
  iVar7 = 0;
  local_70 = (int)param_4 * 0x60 + 4;
  local_cc = 0;
  local_dd = '\0';
  ExceptionList = &local_c;
  local_bc = this;
  do {
    iVar5 = local_88;
    CFastVB__Helper_00426fd0(local_70);
    local_4 = 0;
    if (extraout_EAX == (int *)0x0) {
      local_c4 = (int *)0x0;
    }
    else {
      *extraout_EAX = iVar5;
      eh_vector_constructor_iterator
                (extraout_EAX + 1,0x10,iVar5,&LAB_00572e20,
                 CFastVB__ReleaseBufferAndResetTriplet_0056f260);
      local_c4 = extraout_EAX + 1;
    }
    local_d8 = 0;
    local_4 = 0xffffffff;
    local_c0 = 0;
    local_b4 = local_dd;
    local_b3 = local_dd;
    local_ac = 0;
    CFastVB__Helper_00573d00((int)&local_b4);
    local_4 = 1;
    local_c8 = 0;
    piVar6 = local_c4;
    iVar5 = local_c0;
    if (0 < (int)param_4) {
      do {
        local_d0 = (int *)CFastVB__SelectNextStripTriangle(local_bc,param_2,param_3,(int)unaff_EDI);
        pvVar3 = local_b0;
        if (local_d0 == (int *)0x0) {
          local_dd = '\x01';
          iVar5 = local_d8;
          break;
        }
        RBTree__FindLowerBoundByUIntKey(&local_b4,(int)&local_90,&local_d0,unaff_EDI);
        if (local_90 == pvVar3) {
          CTexture__Helper_00573340(&local_b4,(int)local_14,&local_d0,unaff_EDI);
          iVar5 = CFastVB__FindEdgeRecord(param_3,*local_d0,local_d0[1]);
          CFastVB__Helper_00426fd0(0x2c);
          if (extraout_EAX_00 == (undefined4 *)0x0) {
            local_78 = (undefined4 *)0x0;
          }
          else {
            local_24 = CONCAT31(local_24._1_3_,1);
            *extraout_EAX_00 = local_d0;
            extraout_EAX_00[1] = iVar5;
            extraout_EAX_00[2] = local_24;
            *(char *)(extraout_EAX_00 + 3) = local_dd;
            extraout_EAX_00[4] = 0;
            extraout_EAX_00[5] = 0;
            extraout_EAX_00[6] = 0;
            extraout_EAX_00[7] = iVar7;
            extraout_EAX_00[8] = local_cc;
            *(undefined1 *)(extraout_EAX_00 + 9) = 0;
            extraout_EAX_00[10] = 0;
            local_78 = extraout_EAX_00;
            iVar7 = iVar7 + 1;
            local_cc = local_cc + 1;
          }
          CFastVB__Helper_005736d0(piVar6,piVar6[2],(void *)0x1,(uint)&local_78,unaff_EDI);
          iVar5 = CFastVB__FindEdgeRecord(param_3,*local_d0,local_d0[1]);
          CFastVB__Helper_00426fd0(0x2c);
          if (extraout_EAX_01 == (undefined4 *)0x0) {
            local_7c = (undefined4 *)0x0;
          }
          else {
            local_30 = local_30 & 0xffffff00;
            *extraout_EAX_01 = local_d0;
            extraout_EAX_01[1] = iVar5;
            extraout_EAX_01[2] = local_30;
            *(char *)(extraout_EAX_01 + 3) = local_dd;
            extraout_EAX_01[4] = 0;
            extraout_EAX_01[5] = 0;
            extraout_EAX_01[6] = 0;
            extraout_EAX_01[7] = iVar7;
            extraout_EAX_01[8] = local_cc;
            *(undefined1 *)(extraout_EAX_01 + 9) = 0;
            extraout_EAX_01[10] = 0;
            local_7c = extraout_EAX_01;
            iVar7 = iVar7 + 1;
            local_cc = local_cc + 1;
          }
          CFastVB__Helper_005736d0(piVar6 + 4,piVar6[6],(void *)0x1,(uint)&local_7c,unaff_EDI);
          iVar5 = CFastVB__FindEdgeRecord(param_3,local_d0[1],local_d0[2]);
          CFastVB__Helper_00426fd0(0x2c);
          if (extraout_EAX_02 == (undefined4 *)0x0) {
            local_98 = (undefined4 *)0x0;
          }
          else {
            local_54 = CONCAT31(local_54._1_3_,1);
            *extraout_EAX_02 = local_d0;
            extraout_EAX_02[1] = iVar5;
            extraout_EAX_02[2] = local_54;
            *(char *)(extraout_EAX_02 + 3) = local_dd;
            extraout_EAX_02[4] = 0;
            extraout_EAX_02[5] = 0;
            extraout_EAX_02[6] = 0;
            extraout_EAX_02[7] = iVar7;
            extraout_EAX_02[8] = local_cc;
            *(undefined1 *)(extraout_EAX_02 + 9) = 0;
            extraout_EAX_02[10] = 0;
            local_98 = extraout_EAX_02;
            iVar7 = iVar7 + 1;
            local_cc = local_cc + 1;
          }
          CFastVB__Helper_005736d0(piVar6 + 8,piVar6[10],(void *)0x1,(uint)&local_98,unaff_EDI);
          iVar5 = CFastVB__FindEdgeRecord(param_3,local_d0[1],local_d0[2]);
          CFastVB__Helper_00426fd0(0x2c);
          if (extraout_EAX_03 == (undefined4 *)0x0) {
            local_74 = (undefined4 *)0x0;
          }
          else {
            local_48 = local_48 & 0xffffff00;
            *extraout_EAX_03 = local_d0;
            extraout_EAX_03[1] = iVar5;
            extraout_EAX_03[2] = local_48;
            *(char *)(extraout_EAX_03 + 3) = local_dd;
            extraout_EAX_03[4] = 0;
            extraout_EAX_03[5] = 0;
            extraout_EAX_03[6] = 0;
            extraout_EAX_03[7] = iVar7;
            extraout_EAX_03[8] = local_cc;
            *(undefined1 *)(extraout_EAX_03 + 9) = 0;
            extraout_EAX_03[10] = 0;
            local_74 = extraout_EAX_03;
            iVar7 = iVar7 + 1;
            local_cc = local_cc + 1;
          }
          CFastVB__Helper_005736d0(piVar6 + 0xc,piVar6[0xe],(void *)0x1,(uint)&local_74,unaff_EDI);
          iVar5 = CFastVB__FindEdgeRecord(param_3,local_d0[2],*local_d0);
          CFastVB__Helper_00426fd0(0x2c);
          if (extraout_EAX_04 == (undefined4 *)0x0) {
            local_94 = (undefined4 *)0x0;
          }
          else {
            local_3c = CONCAT31(local_3c._1_3_,1);
            *extraout_EAX_04 = local_d0;
            extraout_EAX_04[1] = iVar5;
            extraout_EAX_04[2] = local_3c;
            *(char *)(extraout_EAX_04 + 3) = local_dd;
            extraout_EAX_04[4] = 0;
            extraout_EAX_04[5] = 0;
            extraout_EAX_04[6] = 0;
            extraout_EAX_04[7] = iVar7;
            extraout_EAX_04[8] = local_cc;
            *(undefined1 *)(extraout_EAX_04 + 9) = 0;
            extraout_EAX_04[10] = 0;
            local_94 = extraout_EAX_04;
            iVar7 = iVar7 + 1;
            local_cc = local_cc + 1;
          }
          this_00 = piVar6 + 0x14;
          CFastVB__Helper_005736d0(piVar6 + 0x10,piVar6[0x12],(void *)0x1,(uint)&local_94,unaff_EDI)
          ;
          iVar5 = CFastVB__FindEdgeRecord(param_3,local_d0[2],*local_d0);
          CFastVB__Helper_00426fd0(0x2c);
          if (extraout_EAX_05 == (undefined4 *)0x0) {
            local_8c = (undefined4 *)0x0;
          }
          else {
            local_18 = local_18 & 0xffffff00;
            *extraout_EAX_05 = local_d0;
            extraout_EAX_05[1] = iVar5;
            extraout_EAX_05[2] = local_18;
            *(char *)(extraout_EAX_05 + 3) = local_dd;
            extraout_EAX_05[4] = 0;
            extraout_EAX_05[5] = 0;
            extraout_EAX_05[6] = 0;
            extraout_EAX_05[7] = iVar7;
            extraout_EAX_05[8] = local_cc;
            *(undefined1 *)(extraout_EAX_05 + 9) = 0;
            extraout_EAX_05[10] = 0;
            local_8c = extraout_EAX_05;
            iVar7 = iVar7 + 1;
            local_cc = local_cc + 1;
          }
          piVar1 = piVar6 + 0x16;
          local_d8 = local_d8 + 6;
          piVar6 = piVar6 + 0x18;
          CFastVB__Helper_005736d0(this_00,*piVar1,(void *)0x1,(uint)&local_8c,unaff_EDI);
        }
        local_c8 = local_c8 + 1;
        iVar5 = local_d8;
      } while (local_c8 < (int)param_4);
    }
    local_c0 = iVar5;
    iVar5 = local_d8;
    if (0 < local_d8) {
      piVar6 = local_c4 + 1;
      do {
        CFastVB__BuildTriangleStripFromSeedRecord(*(void **)*piVar6,(void *)param_3,param_2);
        local_a4 = 0;
        local_a0 = 0;
        local_9c = local_9c & 0xffffff00;
        local_b8 = *(undefined4 **)*piVar6;
        uVar2 = local_b8[8];
        bVar4 = CTexture__Helper_00570cb0(param_2,(void *)param_3,local_b8,&local_a4);
        if (bVar4) {
          do {
            CFastVB__Helper_00426fd0(0x2c);
            if (extraout_EAX_06 == (undefined4 *)0x0) {
              local_b8 = (undefined4 *)0x0;
            }
            else {
              *extraout_EAX_06 = local_a4;
              extraout_EAX_06[1] = local_a0;
              extraout_EAX_06[2] = local_9c;
              *(char *)(extraout_EAX_06 + 3) = local_dd;
              extraout_EAX_06[4] = 0;
              extraout_EAX_06[5] = 0;
              extraout_EAX_06[6] = 0;
              extraout_EAX_06[7] = iVar7;
              extraout_EAX_06[8] = uVar2;
              *(undefined1 *)(extraout_EAX_06 + 9) = 0;
              extraout_EAX_06[10] = 0;
              local_b8 = extraout_EAX_06;
              iVar7 = iVar7 + 1;
            }
            CFastVB__BuildTriangleStripFromSeedRecord(local_b8,(void *)param_3,param_2);
            CFastVB__Helper_005736d0(piVar6 + -1,piVar6[1],(void *)0x1,(uint)&local_b8,unaff_EDI);
            bVar4 = CTexture__Helper_00570cb0(param_2,(void *)param_3,local_b8,&local_a4);
          } while (bVar4);
        }
        piVar6 = piVar6 + 4;
        local_d8 = local_d8 + -1;
        iVar5 = local_c0;
      } while (local_d8 != 0);
    }
    local_c0 = 0;
    local_84 = 0.0;
    local_c8 = 0;
    if (0 < iVar5) {
      piVar6 = local_c4 + 1;
      do {
        dVar8 = CFastVB__Helper_00572570((int)(piVar6 + -1));
        if (*piVar6 == 0) {
          local_6c = 0;
        }
        else {
          local_6c = piVar6[1] - *piVar6 >> 2;
        }
        uStack_68 = 0;
        dVar8 = (double)local_6c * (double)DAT_005e6a3c + dVar8;
        if (local_84 < dVar8) {
          local_c0 = local_c8;
          local_84 = dVar8;
        }
        piVar6 = piVar6 + 4;
        local_c8 = local_c8 + 1;
      } while (local_c8 < iVar5);
    }
    CTexture__Helper_00570be0((int)param_1,(int)(local_c4 + local_c0 * 4));
    local_c8 = 0;
    if (0 < iVar5) {
      piVar6 = local_c4 + 1;
      do {
        if (local_c8 != local_c0) {
          if (*piVar6 == 0) {
            local_d8 = 0;
          }
          else {
            local_d8 = piVar6[1] - *piVar6 >> 2;
          }
          local_d4 = 0;
          if (0 < local_d8) {
            do {
              pvVar3 = *(void **)(*piVar6 + local_d4 * 4);
              if (pvVar3 != (void *)0x0) {
                OID__FreeObject_Callback(*(void **)((int)pvVar3 + 0x10));
                *(undefined4 *)((int)pvVar3 + 0x10) = 0;
                *(undefined4 *)((int)pvVar3 + 0x14) = 0;
                *(undefined4 *)((int)pvVar3 + 0x18) = 0;
                OID__FreeObject_Callback(pvVar3);
              }
              local_d4 = local_d4 + 1;
            } while (local_d4 < local_d8);
          }
        }
        local_c8 = local_c8 + 1;
        piVar6 = piVar6 + 4;
      } while (local_c8 < iVar5);
    }
    if (local_c4 != (int *)0x0) {
      piVar6 = local_c4 + -1;
      CDXLandscape__Helper_0055db0a
                ((int)local_c4,0x10,local_c4[-1],CFastVB__ReleaseBufferAndResetTriplet_0056f260);
      OID__FreeObject_Callback(piVar6);
    }
    local_4 = 0xffffffff;
    CTexture__Helper_00573330(&local_b4,(int)local_60,unaff_EDI);
    CTexture__Helper_00573560(&local_b4,(int)local_64,(void *)*extraout_EAX_07,local_b0,unaff_EDI);
    OID__FreeObject_Callback(local_b0);
    pvVar3 = DAT_009d0c44;
    DAT_009d0c48 = DAT_009d0c48 + -1;
    local_b0 = (void *)0x0;
    local_a8 = 0;
    if ((DAT_009d0c48 == 0) && (DAT_009d0c44 = (void *)0x0, pvVar3 != (void *)0x0)) {
      OID__FreeObject_Callback(pvVar3);
    }
    if (local_dd != '\0') {
      ExceptionList = local_c;
      return;
    }
  } while( true );
}
