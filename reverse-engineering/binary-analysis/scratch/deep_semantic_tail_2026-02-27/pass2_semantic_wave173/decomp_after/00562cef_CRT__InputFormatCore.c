/* address: 0x00562cef */
/* name: CRT__InputFormatCore */
/* signature: int __cdecl CRT__InputFormatCore(int param_1, void * param_2, void * param_3) */


int __cdecl CRT__InputFormatCore(int param_1,void *param_2,void *param_3)

{
  byte bVar1;
  undefined4 *puVar2;
  undefined1 *puVar3;
  byte bVar4;
  uint uVar5;
  uint uVar6;
  undefined1 *in_ECX;
  void *this;
  undefined1 *extraout_ECX;
  void *pvVar7;
  undefined1 *extraout_ECX_00;
  undefined1 *extraout_ECX_01;
  undefined1 *extraout_ECX_02;
  undefined1 *extraout_ECX_03;
  undefined1 *puVar8;
  byte bVar9;
  byte *pbVar10;
  char *pcVar11;
  char *pcVar12;
  byte *pbVar13;
  uint unaff_EDI;
  undefined1 *puVar14;
  int iVar15;
  bool bVar16;
  longlong lVar17;
  undefined1 *puVar18;
  char local_1c8;
  char local_1c7 [351];
  byte local_68 [32];
  undefined4 *local_48;
  undefined2 local_42;
  uint local_40;
  byte local_3c;
  undefined1 local_3b;
  byte local_39;
  int local_38;
  byte *local_34;
  byte *local_30;
  undefined8 local_2c;
  int local_24;
  int local_20;
  byte local_1c;
  char local_1b;
  char local_1a;
  char local_19;
  undefined1 *local_18;
  char local_13;
  char local_12;
  char local_11;
  int local_10;
  char local_9;
  undefined *local_8;

  local_19 = '\0';
  bVar1 = *(byte *)param_2;
  local_8 = (undefined1 *)0x0;
  local_38 = 0;
  pbVar10 = param_2;
  puVar8 = PTR_DAT_00653890;
  do {
    PTR_DAT_00653890 = puVar8;
    if (bVar1 == 0) {
LAB_005636f5:
      if (local_18 == (undefined1 *)0xffffffff) {
LAB_005636fb:
        if ((local_38 == 0) && (local_19 == '\0')) {
          local_38 = -1;
        }
      }
      return local_38;
    }
    if (DAT_00653a9c < 2) {
      uVar5 = (byte)puVar8[(uint)bVar1 * 2] & 8;
    }
    else {
      puVar8 = (undefined1 *)0x8;
      uVar5 = CRT__GetCharTypeMask_Compat(in_ECX,(uint)bVar1,8,unaff_EDI);
    }
    if (uVar5 != 0) {
      local_8 = local_8 + -1;
      iVar15 = param_1;
      uVar5 = CRT__GetNonSpaceCharFromStream(&local_8,(void *)param_1);
      CRT__UngetCharIfNotEof(uVar5,iVar15);
      uVar5 = CRT__IsCharTypeMask0x08(this,(void *)(uint)pbVar10[1],uVar5);
      puVar8 = extraout_ECX;
      pbVar13 = pbVar10;
      while (pbVar10 = pbVar13 + 1, uVar5 != 0) {
        puVar14 = (undefined1 *)(uint)pbVar13[2];
        uVar5 = CRT__IsCharTypeMask0x08(puVar8,(undefined1 *)(uint)pbVar13[2],unaff_EDI);
        puVar8 = puVar14;
        pbVar13 = pbVar10;
      }
    }
    if (*pbVar10 == 0x25) {
      local_39 = 0;
      local_1c = 0;
      local_1b = '\0';
      local_12 = '\0';
      local_13 = '\0';
      local_1a = '\0';
      puVar14 = (undefined1 *)0x0;
      local_9 = '\0';
      local_20 = 0;
      local_24 = 0;
      local_10 = 0;
      local_11 = '\x01';
      local_34 = (byte *)0x0;
      do {
        uVar5 = (uint)pbVar10[1];
        param_2 = pbVar10 + 1;
        if (DAT_00653a9c < 2) {
          uVar6 = (byte)PTR_DAT_00653890[uVar5 * 2] & 4;
          puVar8 = PTR_DAT_00653890;
        }
        else {
          puVar18 = (undefined1 *)0x4;
          uVar6 = CRT__GetCharTypeMask_Compat(puVar8,uVar5,4,unaff_EDI);
          puVar8 = puVar18;
        }
        if (uVar6 == 0) {
          if (uVar5 < 0x4f) {
            if (uVar5 != 0x4e) {
              if (uVar5 == 0x2a) {
                local_12 = local_12 + '\x01';
              }
              else if (uVar5 != 0x46) {
                if (uVar5 == 0x49) {
                  if ((pbVar10[2] != 0x36) || (pbVar10[3] != 0x34)) goto LAB_00562e4a;
                  local_34 = local_34 + 1;
                  local_2c = 0;
                  param_2 = pbVar10 + 3;
                }
                else if (uVar5 == 0x4c) {
                  local_11 = local_11 + '\x01';
                }
                else {
LAB_00562e4a:
                  local_13 = local_13 + '\x01';
                }
              }
            }
          }
          else if (uVar5 == 0x68) {
            local_11 = local_11 + -1;
            local_9 = local_9 + -1;
          }
          else {
            if (uVar5 == 0x6c) {
              local_11 = local_11 + '\x01';
            }
            else if (uVar5 != 0x77) goto LAB_00562e4a;
            local_9 = local_9 + '\x01';
          }
        }
        else {
          local_24 = local_24 + 1;
          local_10 = (uVar5 - 0x30) + local_10 * 10;
        }
        pbVar10 = param_2;
      } while (local_13 == '\0');
      puVar2 = param_3;
      if (local_12 == '\0') {
        local_30 = *(byte **)param_3;
        puVar2 = (undefined4 *)((int)param_3 + 4);
        local_48 = param_3;
      }
      param_3 = puVar2;
      local_13 = '\0';
      if (local_9 == '\0') {
        if ((*(byte *)param_2 == 0x53) || (*(byte *)param_2 == 0x43)) {
          local_9 = '\x01';
        }
        else {
          local_9 = -1;
        }
      }
      uVar5 = *(byte *)param_2 | 0x20;
      local_40 = uVar5;
      if (uVar5 != 0x6e) {
        if ((uVar5 == 99) || (uVar5 == 0x7b)) {
          local_8 = local_8 + 1;
          puVar8 = (undefined1 *)param_1;
          local_18 = (undefined1 *)CRT__GetCharFromStream((void *)param_1);
        }
        else {
          puVar8 = (undefined1 *)param_1;
          local_18 = (undefined1 *)CRT__GetNonSpaceCharFromStream(&local_8,(void *)param_1);
        }
      }
      if ((local_24 != 0) && (local_10 == 0)) {
LAB_005636d5:
        local_8 = local_8 + -1;
        CRT__UngetCharIfNotEof((int)local_18,param_1);
        goto LAB_005636f5;
      }
      if (uVar5 < 0x70) {
        if (uVar5 == 0x6f) {
LAB_00563402:
          if (local_18 == (undefined1 *)0x2d) {
            local_1b = '\x01';
          }
          else if (local_18 != (undefined1 *)0x2b) goto LAB_00563437;
          local_10 = local_10 + -1;
          if ((local_10 == 0) && (local_24 != 0)) {
            local_13 = '\x01';
          }
          else {
            local_8 = local_8 + 1;
            puVar8 = (undefined1 *)param_1;
            local_18 = (undefined1 *)CRT__GetCharFromStream((void *)param_1);
          }
          goto LAB_00563437;
        }
        if (uVar5 != 99) {
          if (uVar5 == 100) goto LAB_00563402;
          if (uVar5 < 0x65) {
LAB_0056317a:
            if ((undefined1 *)(uint)*(byte *)param_2 != local_18) goto LAB_005636d5;
            local_19 = local_19 + -1;
            if (local_12 == '\0') {
              param_3 = local_48;
            }
            goto LAB_00563656;
          }
          if (0x67 < uVar5) {
            if (uVar5 == 0x69) {
              uVar5 = 100;
              goto LAB_00562f38;
            }
            if (uVar5 != 0x6e) goto LAB_0056317a;
            puVar14 = local_8;
            lVar17 = local_2c;
            if (local_12 != '\0') goto LAB_00563656;
            goto LAB_00563630;
          }
          pcVar11 = &local_1c8;
          if (local_18 == (undefined1 *)0x2d) {
            local_1c8 = '-';
            pcVar11 = local_1c7;
LAB_00562f6e:
            local_10 = local_10 + -1;
            local_8 = local_8 + 1;
            puVar8 = (undefined1 *)param_1;
            local_18 = (undefined1 *)CRT__GetCharFromStream((void *)param_1);
          }
          else if (local_18 == (undefined1 *)0x2b) goto LAB_00562f6e;
          if ((local_24 == 0) || (0x15d < local_10)) {
            local_10 = 0x15d;
          }
          while( true ) {
            puVar14 = local_18;
            if (DAT_00653a9c < 2) {
              uVar5 = (byte)PTR_DAT_00653890[(int)local_18 * 2] & 4;
            }
            else {
              uVar5 = CRT__GetCharTypeMask_Compat(puVar8,(int)local_18,4,unaff_EDI);
            }
            if ((uVar5 == 0) ||
               (iVar15 = local_10 + -1, bVar16 = local_10 == 0, local_10 = iVar15, bVar16)) break;
            local_20 = local_20 + 1;
            *pcVar11 = (char)puVar14;
            pcVar11 = pcVar11 + 1;
            local_8 = local_8 + 1;
            puVar8 = (undefined1 *)param_1;
            local_18 = (undefined1 *)CRT__GetCharFromStream((void *)param_1);
          }
          if ((DAT_00653aa0 == (char)puVar14) &&
             (iVar15 = local_10 + -1, bVar16 = local_10 != 0, local_10 = iVar15, bVar16)) {
            local_8 = local_8 + 1;
            pvVar7 = (void *)param_1;
            puVar14 = (undefined1 *)CRT__GetCharFromStream((void *)param_1);
            *pcVar11 = DAT_00653aa0;
            while( true ) {
              pcVar11 = pcVar11 + 1;
              local_18 = puVar14;
              if (DAT_00653a9c < 2) {
                uVar5 = (byte)PTR_DAT_00653890[(int)puVar14 * 2] & 4;
              }
              else {
                uVar5 = CRT__GetCharTypeMask_Compat(pvVar7,(int)puVar14,4,unaff_EDI);
              }
              if ((uVar5 == 0) ||
                 (iVar15 = local_10 + -1, bVar16 = local_10 == 0, local_10 = iVar15, bVar16)) break;
              local_20 = local_20 + 1;
              *pcVar11 = (char)puVar14;
              local_8 = local_8 + 1;
              pvVar7 = (void *)param_1;
              puVar14 = (undefined1 *)CRT__GetCharFromStream((void *)param_1);
            }
          }
          pcVar12 = pcVar11;
          if ((local_20 != 0) &&
             (((puVar14 == &DAT_00000065 || (puVar14 == (undefined1 *)0x45)) &&
              (iVar15 = local_10 + -1, bVar16 = local_10 != 0, local_10 = iVar15, bVar16)))) {
            *pcVar11 = 'e';
            pcVar12 = pcVar11 + 1;
            local_8 = local_8 + 1;
            pvVar7 = (void *)param_1;
            puVar14 = (undefined1 *)CRT__GetCharFromStream((void *)param_1);
            local_18 = puVar14;
            if (puVar14 == (undefined1 *)0x2d) {
              *pcVar12 = '-';
              pcVar12 = pcVar11 + 2;
LAB_00563095:
              bVar16 = local_10 != 0;
              local_10 = local_10 + -1;
              if (bVar16) goto LAB_005630a4;
              local_10 = 0;
            }
            else if (puVar14 == (undefined1 *)0x2b) goto LAB_00563095;
            while( true ) {
              if (DAT_00653a9c < 2) {
                uVar5 = (byte)PTR_DAT_00653890[(int)puVar14 * 2] & 4;
              }
              else {
                uVar5 = CRT__GetCharTypeMask_Compat(pvVar7,(int)puVar14,4,unaff_EDI);
              }
              if ((uVar5 == 0) ||
                 (iVar15 = local_10 + -1, bVar16 = local_10 == 0, local_10 = iVar15, bVar16)) break;
              local_20 = local_20 + 1;
              *pcVar12 = (char)puVar14;
              pcVar12 = pcVar12 + 1;
LAB_005630a4:
              local_8 = local_8 + 1;
              pvVar7 = (void *)param_1;
              puVar14 = (undefined1 *)CRT__GetCharFromStream((void *)param_1);
              local_18 = puVar14;
            }
          }
          local_8 = local_8 + -1;
          puVar8 = (undefined1 *)param_1;
          CRT__UngetCharIfNotEof((int)puVar14,param_1);
          if (local_20 != 0) {
            if (local_12 == '\0') {
              local_38 = local_38 + 1;
              *pcVar12 = '\0';
              (*(code *)PTR_ControlsUI__Helper_00569cb8_00653660)(local_11 + -1,local_30,&local_1c8)
              ;
              puVar8 = extraout_ECX_00;
            }
            goto LAB_00563656;
          }
          goto LAB_005636f5;
        }
        if (local_24 == 0) {
          local_10 = local_10 + 1;
          local_24 = 1;
        }
        if ('\0' < local_9) {
          local_1a = '\x01';
        }
        pcVar11 = &DAT_00653888;
LAB_0056325b:
        local_1c = 0xff;
        pbVar10 = (byte *)pcVar11;
        pbVar13 = param_2;
LAB_0056325f:
        param_2 = pbVar13;
        _memset(local_68,0,0x20);
        if ((local_40 == 0x7b) && (*pbVar10 == 0x5d)) {
          uVar5 = 0x5d;
          local_68[0xb] = 0x20;
          pbVar10 = pbVar10 + 1;
        }
        else {
          uVar5 = (uint)local_39;
        }
        while (pbVar13 = local_30, bVar1 = *pbVar10, bVar1 != 0x5d) {
          if (((bVar1 == 0x2d) && (bVar9 = (byte)uVar5, bVar9 != 0)) &&
             (bVar4 = pbVar10[1], bVar4 != 0x5d)) {
            if (bVar4 <= bVar9) {
              uVar5 = (uint)bVar4;
              bVar4 = bVar9;
            }
            if ((byte)uVar5 <= bVar4) {
              iVar15 = (bVar4 - uVar5) + 1;
              do {
                local_68[uVar5 >> 3] = local_68[uVar5 >> 3] | '\x01' << ((byte)uVar5 & 7);
                uVar5 = uVar5 + 1;
                iVar15 = iVar15 + -1;
              } while (iVar15 != 0);
            }
            uVar5 = 0;
            pbVar10 = pbVar10 + 2;
          }
          else {
            uVar5 = (uint)bVar1;
            local_68[bVar1 >> 3] = local_68[bVar1 >> 3] | '\x01' << (bVar1 & 7);
            pbVar10 = pbVar10 + 1;
          }
        }
        if (*pbVar10 == 0) goto LAB_005636f5;
        if (local_40 == 0x7b) {
          param_2 = pbVar10;
        }
        local_8 = local_8 + -1;
        local_34 = local_30;
        puVar8 = (undefined1 *)param_1;
        CRT__UngetCharIfNotEof((int)local_18,param_1);
        while( true ) {
          if ((local_24 != 0) &&
             (iVar15 = local_10 + -1, bVar16 = local_10 == 0, local_10 = iVar15, bVar16))
          goto LAB_005633c4;
          local_8 = local_8 + 1;
          local_18 = (undefined1 *)CRT__GetCharFromStream((void *)param_1);
          if (local_18 == (undefined1 *)0xffffffff) break;
          bVar1 = (byte)local_18;
          puVar8 = (undefined1 *)(int)(char)(local_68[(int)local_18 >> 3] ^ local_1c);
          if (((uint)puVar8 & 1 << (bVar1 & 7)) == 0) break;
          if (local_12 == '\0') {
            if (local_1a == '\0') {
              *pbVar13 = bVar1;
              pbVar13 = pbVar13 + 1;
              local_30 = pbVar13;
            }
            else {
              local_3c = bVar1;
              if ((PTR_DAT_00653890[((uint)local_18 & 0xff) * 2 + 1] & 0x80) != 0) {
                local_8 = local_8 + 1;
                uVar5 = CRT__GetCharFromStream((void *)param_1);
                local_3b = (undefined1)uVar5;
              }
              CRT__MultiByteToWideChar_ThreadSafe((int)&local_42,(int)&local_3c,DAT_00653a9c);
              *(undefined2 *)pbVar13 = local_42;
              pbVar13 = pbVar13 + 2;
              puVar8 = extraout_ECX_01;
              local_30 = pbVar13;
            }
          }
          else {
            local_34 = local_34 + 1;
          }
        }
        local_8 = local_8 + -1;
        puVar8 = (undefined1 *)param_1;
        CRT__UngetCharIfNotEof((int)local_18,param_1);
LAB_005633c4:
        if (local_34 == pbVar13) goto LAB_005636f5;
        if ((local_12 == '\0') && (local_38 = local_38 + 1, local_40 != 99)) {
          if (local_1a == '\0') {
            *local_30 = 0;
          }
          else {
            local_30[0] = 0;
            local_30[1] = 0;
          }
        }
      }
      else {
        if (uVar5 == 0x70) {
          local_11 = '\x01';
          goto LAB_00563402;
        }
        if (uVar5 == 0x73) {
          if ('\0' < local_9) {
            local_1a = '\x01';
          }
          pcVar11 = s_____00653880;
          goto LAB_0056325b;
        }
        if (uVar5 == 0x75) goto LAB_00563402;
        if (uVar5 != 0x78) {
          if (uVar5 != 0x7b) goto LAB_0056317a;
          if ('\0' < local_9) {
            local_1a = '\x01';
          }
          pbVar10 = (byte *)((int)param_2 + 1);
          pbVar13 = pbVar10;
          if (*pbVar10 == 0x5e) {
            pcVar11 = (char *)((int)param_2 + 2);
            param_2 = pbVar10;
            goto LAB_0056325b;
          }
          goto LAB_0056325f;
        }
LAB_00562f38:
        if (local_18 == (undefined1 *)0x2d) {
          local_1b = '\x01';
LAB_005631c7:
          local_10 = local_10 + -1;
          if ((local_10 == 0) && (local_24 != 0)) {
            local_13 = '\x01';
          }
          else {
            local_8 = local_8 + 1;
            puVar8 = (undefined1 *)param_1;
            local_18 = (undefined1 *)CRT__GetCharFromStream((void *)param_1);
          }
        }
        else if (local_18 == (undefined1 *)0x2b) goto LAB_005631c7;
        if (local_18 == (undefined1 *)0x30) {
          local_8 = local_8 + 1;
          puVar8 = (undefined1 *)param_1;
          local_18 = (undefined1 *)CRT__GetCharFromStream((void *)param_1);
          if (((char)local_18 == 'x') || ((char)local_18 == 'X')) {
            local_8 = local_8 + 1;
            puVar8 = (undefined1 *)param_1;
            local_18 = (undefined1 *)CRT__GetCharFromStream((void *)param_1);
            uVar5 = 0x78;
          }
          else {
            local_20 = 1;
            if (uVar5 == 0x78) {
              local_8 = local_8 + -1;
              puVar8 = (undefined1 *)param_1;
              CRT__UngetCharIfNotEof((int)local_18,param_1);
              local_18 = (undefined1 *)0x30;
            }
            else {
              uVar5 = 0x6f;
            }
          }
        }
LAB_00563437:
        lVar17 = local_2c;
        if (local_34 == (byte *)0x0) {
          if (local_13 == '\0') {
            while ((puVar18 = local_18, uVar5 != 0x78 && (uVar5 != 0x70))) {
              if (DAT_00653a9c < 2) {
                uVar6 = (byte)PTR_DAT_00653890[(int)local_18 * 2] & 4;
              }
              else {
                puVar3 = (undefined1 *)0x4;
                uVar6 = CRT__GetCharTypeMask_Compat(puVar8,(int)local_18,4,unaff_EDI);
                puVar8 = puVar3;
              }
              if (uVar6 == 0) goto LAB_005635fe;
              if (uVar5 == 0x6f) {
                if (0x37 < (int)puVar18) goto LAB_005635fe;
                iVar15 = (int)puVar14 << 3;
              }
              else {
                iVar15 = (int)puVar14 * 10;
              }
LAB_005635d6:
              local_20 = local_20 + 1;
              puVar14 = puVar18 + iVar15 + -0x30;
              if ((local_24 != 0) && (local_10 = local_10 + -1, lVar17 = local_2c, local_10 == 0))
              goto LAB_0056360c;
              local_8 = local_8 + 1;
              puVar8 = (undefined1 *)param_1;
              local_18 = (undefined1 *)CRT__GetCharFromStream((void *)param_1);
            }
            if (DAT_00653a9c < 2) {
              uVar6 = (byte)PTR_DAT_00653890[(int)local_18 * 2] & 0x80;
            }
            else {
              uVar6 = CRT__GetCharTypeMask_Compat(puVar8,(int)local_18,0x80,unaff_EDI);
            }
            if (uVar6 != 0) {
              iVar15 = (int)puVar14 << 4;
              puVar8 = puVar18;
              puVar18 = (undefined1 *)CRT__NormalizeDigitForBase((uint)puVar18);
              local_18 = puVar18;
              goto LAB_005635d6;
            }
LAB_005635fe:
            local_8 = local_8 + -1;
            puVar8 = (undefined1 *)param_1;
            CRT__UngetCharIfNotEof((int)puVar18,param_1);
            lVar17 = local_2c;
          }
LAB_0056360c:
          if (local_1b != '\0') {
            puVar14 = (undefined1 *)-(int)puVar14;
          }
        }
        else {
          if (local_13 == '\0') {
            while (puVar18 = local_18, uVar5 != 0x78) {
              if (DAT_00653a9c < 2) {
                uVar6 = (byte)PTR_DAT_00653890[(int)local_18 * 2] & 4;
              }
              else {
                uVar6 = CRT__GetCharTypeMask_Compat(puVar8,(int)local_18,4,unaff_EDI);
              }
              if (uVar6 == 0) goto LAB_00563520;
              if (uVar5 == 0x6f) {
                if (0x37 < (int)puVar18) goto LAB_00563520;
                lVar17 = __allshl();
                puVar8 = extraout_ECX_02;
              }
              else {
                lVar17 = __allmul(local_2c,10,0);
                puVar8 = extraout_ECX_03;
              }
LAB_005634f2:
              local_20 = local_20 + 1;
              local_2c = lVar17 + (int)(puVar18 + -0x30);
              if ((local_24 != 0) && (local_10 = local_10 + -1, lVar17 = local_2c, local_10 == 0))
              goto LAB_0056352e;
              local_8 = local_8 + 1;
              puVar8 = (undefined1 *)param_1;
              local_18 = (undefined1 *)CRT__GetCharFromStream((void *)param_1);
            }
            if (DAT_00653a9c < 2) {
              uVar6 = (byte)PTR_DAT_00653890[(int)local_18 * 2] & 0x80;
            }
            else {
              uVar6 = CRT__GetCharTypeMask_Compat(puVar8,(int)local_18,0x80,unaff_EDI);
            }
            if (uVar6 != 0) {
              lVar17 = __allshl();
              puVar8 = puVar18;
              local_2c = lVar17;
              puVar18 = (undefined1 *)CRT__NormalizeDigitForBase((uint)puVar18);
              local_18 = puVar18;
              lVar17 = local_2c;
              goto LAB_005634f2;
            }
LAB_00563520:
            local_8 = local_8 + -1;
            puVar8 = (undefined1 *)param_1;
            CRT__UngetCharIfNotEof((int)puVar18,param_1);
            lVar17 = local_2c;
          }
LAB_0056352e:
          local_2c._4_4_ = (undefined1 *)((ulonglong)lVar17 >> 0x20);
          local_2c._0_4_ = (int)lVar17;
          if (local_1b != '\0') {
            puVar8 = (undefined1 *)-((int)local_2c._4_4_ + (uint)((int)local_2c != 0));
            lVar17 = CONCAT44(puVar8,-(int)local_2c);
          }
        }
        if (uVar5 == 0x46) {
          local_20 = 0;
        }
        if (local_20 == 0) goto LAB_005636f5;
        local_2c = lVar17;
        if (local_12 == '\0') {
          local_38 = local_38 + 1;
LAB_00563630:
          local_2c._4_4_ = (undefined1 *)((ulonglong)lVar17 >> 0x20);
          local_2c = lVar17;
          if (local_34 == (byte *)0x0) {
            if (local_11 == '\0') {
              *(short *)local_30 = (short)puVar14;
            }
            else {
              *(undefined1 **)local_30 = puVar14;
            }
          }
          else {
            *(longlong *)local_30 = lVar17;
            puVar8 = local_2c._4_4_;
          }
        }
      }
LAB_00563656:
      local_19 = local_19 + '\x01';
      param_2 = (void *)((int)param_2 + 1);
      in_ECX = puVar8;
    }
    else {
      local_8 = local_8 + 1;
      puVar8 = (undefined1 *)CRT__GetCharFromStream((void *)param_1);
      param_2 = pbVar10 + 1;
      local_18 = puVar8;
      if ((undefined1 *)(uint)*pbVar10 != puVar8) goto LAB_005636d5;
      in_ECX = PTR_DAT_00653890;
      if ((PTR_DAT_00653890[((uint)puVar8 & 0xff) * 2 + 1] & 0x80) != 0) {
        local_8 = local_8 + 1;
        puVar14 = (undefined1 *)CRT__GetCharFromStream((void *)param_1);
        in_ECX = (undefined1 *)(uint)*(byte *)param_2;
        param_2 = pbVar10 + 2;
        if (in_ECX != puVar14) {
          local_8 = local_8 + -1;
          CRT__UngetCharIfNotEof((int)puVar14,param_1);
          local_8 = local_8 + -1;
          CRT__UngetCharIfNotEof((int)puVar8,param_1);
          goto LAB_005636f5;
        }
        local_8 = local_8 + -1;
      }
    }
    if ((local_18 == (undefined1 *)0xffffffff) &&
       ((*(char *)param_2 != '%' || (*(char *)((int)param_2 + 1) != 'n')))) goto LAB_005636fb;
    bVar1 = *(byte *)param_2;
    pbVar10 = param_2;
    puVar8 = PTR_DAT_00653890;
  } while( true );
}
