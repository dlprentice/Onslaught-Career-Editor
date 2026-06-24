/* address: 0x00549570 */
/* name: CMeshRenderer__RenderMeshCore */
/* signature: void CMeshRenderer__RenderMeshCore(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CMeshRenderer__RenderMeshCore(void)

{
  float fVar1;
  float fVar2;
  bool bVar3;
  int iVar4;
  undefined4 uVar5;
  int *piVar6;
  float *pfVar7;
  float *pfVar8;
  undefined4 *puVar9;
  uint uVar10;
  int iVar11;
  undefined4 *puVar12;
  int iVar13;
  void *pvVar14;
  float *pfVar15;
  undefined4 *puVar16;
  void *unaff_EDI;
  undefined4 *puVar17;
  float10 fVar18;
  double dVar19;
  double dVar20;
  float fVar21;
  undefined1 *puStack00000004;
  int iStack00000008;
  float *pfStack0000000c;
  int iVar22;
  float in_stack_00000024;
  undefined4 *in_stack_00000028;
  float fStack0000002c;
  undefined4 *in_stack_00000034;
  float in_stack_00000040;
  float in_stack_0000004c;
  float in_stack_00000050;
  float in_stack_00000054;
  float in_stack_00000058;
  float in_stack_0000005c;
  float in_stack_00000060;
  float in_stack_00000064;
  float in_stack_00000068;
  undefined4 *in_stack_0000006c;
  float in_stack_00000070;
  float in_stack_00000074;
  float in_stack_00000078;
  float in_stack_0000007c;
  float in_stack_00000080;
  float in_stack_00000084;
  float in_stack_00000088;
  float in_stack_0000008c;
  float in_stack_00000090;
  float in_stack_00000094;
  float in_stack_00000098;
  undefined4 *in_stack_0000009c;
  float in_stack_000000a0;
  float in_stack_000000a4;
  float in_stack_000000a8;
  float in_stack_000000ac;
  float in_stack_000000b0;
  undefined4 *in_stack_000000b4;
  float in_stack_000000b8;
  int in_stack_000000bc;
  int iStack000000c0;
  int iStack000000c4;
  float in_stack_000000c8;
  float in_stack_000000cc;
  float in_stack_000000d0;
  float in_stack_000000d4;
  float in_stack_000000d8;
  float in_stack_000000dc;
  float in_stack_000000e0;
  float in_stack_000000e4;
  float in_stack_000000e8;
  float in_stack_000000ec;
  float in_stack_000000f0;
  float in_stack_000000f4;
  float in_stack_000000f8;
  float in_stack_000000fc;
  float in_stack_00000100;
  float in_stack_00000104;
  float in_stack_00000108;
  float in_stack_0000010c;
  float in_stack_00000110;
  float in_stack_00000114;
  float in_stack_00000118;
  float in_stack_0000011c;
  float in_stack_00000120;
  float in_stack_00000124;
  float in_stack_00000128;
  float in_stack_0000012c;
  float in_stack_00000130;
  float in_stack_00000134;
  float in_stack_00000138;
  undefined4 *in_stack_0000013c;
  float in_stack_00000140;
  float in_stack_00000144;
  float in_stack_00000148;
  float in_stack_0000014c;
  float in_stack_00000154;
  undefined4 *in_stack_00000158;
  float in_stack_0000015c;
  float in_stack_00000164;
  float in_stack_00000168;
  float in_stack_0000016c;
  float in_stack_00000170;
  float in_stack_00000174;
  float in_stack_00000178;
  float in_stack_0000017c;
  float in_stack_00000180;
  float in_stack_00000184;
  float in_stack_00000188;
  float in_stack_0000018c;
  float in_stack_00000190;
  float in_stack_00000194;
  float in_stack_00000198;
  float in_stack_0000019c;
  float in_stack_000001a0;
  float in_stack_000001a4;
  float in_stack_000001a8;
  float in_stack_000001ac;
  float in_stack_000001b0;
  float in_stack_000001b4;
  float in_stack_000001b8;
  float in_stack_000001bc;
  float in_stack_000001c0;
  float in_stack_000001c4;
  float in_stack_000001c8;
  float in_stack_000001cc;
  float in_stack_000001d0;
  float in_stack_000001d4;
  float in_stack_000001d8;
  float in_stack_000001dc;
  float in_stack_000001e0;
  float in_stack_000001e4;
  float in_stack_000001e8;
  float in_stack_000001ec;
  float in_stack_000001f0;
  float in_stack_000001f4;
  float *in_stack_00001e68;
  int in_stack_00001e6c;
  int *in_stack_00001e70;
  void *in_stack_00001e7c;
  int *in_stack_00001e80;
  undefined1 *puVar23;

  CDXTexture__Helper_0055def0();
  iVar13 = *(int *)(in_stack_00001e6c + 0x8c);
  if (iVar13 != 1) {
    if (iVar13 == 3) {
      iVar13 = -1;
      fVar21 = 0.0;
      piVar6 = in_stack_00001e70;
      if (in_stack_00001e70 != (int *)0x0) {
        iVar13 = (**(code **)(*in_stack_00001e70 + 0x1c))();
      }
      uVar10 = (uint)in_stack_00001e7c & 8;
      if (uVar10 == 8) {
        iVar13 = DAT_00704e5c;
      }
      if (((*(int *)(in_stack_00001e6c + 0xb8) < 2) ||
          (*(int *)(*(int *)(in_stack_00001e6c + 0x128) + 0x14) == 0)) || (iVar13 < 0)) {
        dVar20 = CDXEngine__Helper_0055dfe7(0.0);
        iVar13 = (int)(longlong)ROUND(dVar20);
        puStack00000004 = (undefined1 *)0x3f800000;
      }
      else {
        if (in_stack_00001e70 != (int *)0x0) {
          fVar18 = (float10)(**(code **)(*in_stack_00001e70 + 0x18))();
          fVar21 = (float)fVar18;
        }
        if (uVar10 == 8) {
          fVar21 = DAT_00704e58;
        }
        iVar11 = *(int *)(*(int *)(in_stack_00001e6c + 0x128) + 0x18);
        fVar21 = (float)*(int *)(iVar11 + iVar13 * 0x24 + 0x14) +
                 (float)*(int *)(iVar11 + 0x1c + iVar13 * 0x24) * fVar21;
        if (in_stack_00001e80 != (int *)0x0) {
          (**(code **)(*in_stack_00001e80 + 0x14))();
        }
        CDXEngine__Helper_0055dfe7((double)fVar21);
        CDXEngine__Helper_0055dfe7((double)fVar21);
        puStack00000004 = (undefined1 *)0x0;
        dVar20 = CDXEngine__Helper_0055dfe7(0.0);
        iVar13 = (int)(longlong)ROUND(dVar20);
        dVar20 = CDXEngine__Helper_0055dfe7(0.0);
        if ((int)(longlong)ROUND(dVar20) < iVar13 + 1) {
          CDXEngine__Helper_0055dfe7(0.0);
        }
      }
      _iStack000000c0 =
           CONCAT44(iStack000000c4,*(undefined4 *)(*(int *)(in_stack_00001e6c + 0x84) + iVar13 * 4))
      ;
      CDXEngine__Helper_0055dfe7((double)(float)puStack00000004);
      CMCMech__Helper_004b0fb0();
      CUnitAI__Unk_0049bc80(&stack0x000002a4,&stack0x00000024,unaff_EDI);
      in_stack_00000028 = in_stack_00000034;
      CUnitAI__Unk_0049bc40(&stack0x000002a4);
      CMCBuggy__DivideVector();
      CMCBuggy__DivideVector();
      CMCBuggy__DivideVector();
      iVar13 = 0;
      if (0 < *(int *)(in_stack_00001e6c + 0xc0)) {
        in_stack_0000009c = (undefined4 *)&stack0x00000554;
        do {
          in_stack_00000028 = (undefined4 *)0x0;
          in_stack_00000024 = 0.0;
          CMCMech__Helper_004b0fb0();
          in_stack_00000028 = (undefined4 *)0x0;
          in_stack_00000024 = 1.4013e-45;
          CMCMech__Helper_004b0fb0();
          in_stack_0000004c =
               in_stack_00000174 * in_stack_00000070 +
               in_stack_00000078 * in_stack_00000194 + in_stack_00000074 * in_stack_00000184;
          in_stack_00000050 =
               in_stack_00000070 * in_stack_00000178 +
               in_stack_00000078 * in_stack_00000198 + in_stack_00000074 * in_stack_00000188;
          in_stack_00000028 = (undefined4 *)&LAB_00402d20;
          in_stack_00000024 = 4.2039e-45;
          in_stack_00000054 =
               in_stack_00000070 * in_stack_0000017c +
               in_stack_00000078 * in_stack_0000019c + in_stack_00000074 * in_stack_0000018c;
          in_stack_00000144 =
               in_stack_00000174 * in_stack_00000060 +
               in_stack_00000068 * in_stack_00000194 + in_stack_00000064 * in_stack_00000184;
          in_stack_00000148 =
               in_stack_00000068 * in_stack_00000198 +
               in_stack_00000060 * in_stack_00000178 + in_stack_00000064 * in_stack_00000188;
          in_stack_0000014c =
               in_stack_00000068 * in_stack_0000019c +
               in_stack_00000060 * in_stack_0000017c + in_stack_00000064 * in_stack_0000018c;
          vector_constructor_iterator_nothrow(&stack0x00000240,0x10,3,&LAB_00402d20);
          in_stack_000000c8 = in_stack_000000c8 - in_stack_00000154;
          in_stack_000000cc = in_stack_000000cc - (float)in_stack_00000158;
          puVar9 = (undefined4 *)&stack0x00000240;
          puVar12 = &stack0x00000174;
          for (iVar11 = 0xc; iVar11 != 0; iVar11 = iVar11 + -1) {
            *puVar12 = *puVar9;
            puVar9 = puVar9 + 1;
            puVar12 = puVar12 + 1;
          }
          in_stack_000000d0 = in_stack_000000d0 - in_stack_0000015c;
          in_stack_000000a4 =
               in_stack_00000060 * in_stack_000000c8 +
               in_stack_00000068 * in_stack_000000d0 + in_stack_00000064 * in_stack_000000cc;
          in_stack_000000d4 = in_stack_000000b0;
          in_stack_000000a8 =
               in_stack_00000070 * in_stack_000000c8 +
               in_stack_00000074 * in_stack_000000cc + in_stack_00000078 * in_stack_000000d0;
          in_stack_000000ac =
               in_stack_00000080 * in_stack_000000c8 +
               in_stack_00000084 * in_stack_000000cc + in_stack_00000088 * in_stack_000000d0;
          in_stack_000000ec =
               in_stack_00000080 * in_stack_00000104 +
               in_stack_00000084 * in_stack_00000114 + in_stack_00000088 * in_stack_00000124;
          in_stack_000000f0 =
               in_stack_00000080 * in_stack_00000108 +
               in_stack_00000084 * in_stack_00000118 + in_stack_00000088 * in_stack_00000128;
          in_stack_000000f4 =
               in_stack_00000080 * in_stack_0000010c +
               in_stack_00000084 * in_stack_0000011c + in_stack_00000088 * in_stack_0000012c;
          in_stack_00000028 = (undefined4 *)&LAB_00402d20;
          in_stack_00000024 = 4.2039e-45;
          in_stack_00000164 =
               in_stack_00000070 * in_stack_00000104 +
               in_stack_00000078 * in_stack_00000124 + in_stack_00000074 * in_stack_00000114;
          in_stack_00000168 =
               in_stack_00000070 * in_stack_00000108 +
               in_stack_00000078 * in_stack_00000128 + in_stack_00000074 * in_stack_00000118;
          in_stack_0000016c =
               in_stack_00000070 * in_stack_0000010c +
               in_stack_00000078 * in_stack_0000012c + in_stack_00000074 * in_stack_0000011c;
          in_stack_000000dc =
               in_stack_00000064 * in_stack_00000114 +
               in_stack_00000060 * in_stack_00000104 + in_stack_00000068 * in_stack_00000124;
          in_stack_000000e0 =
               in_stack_00000068 * in_stack_00000128 +
               in_stack_00000060 * in_stack_00000108 + in_stack_00000064 * in_stack_00000118;
          in_stack_000000e4 =
               in_stack_00000068 * in_stack_0000012c +
               in_stack_00000060 * in_stack_0000010c + in_stack_00000064 * in_stack_0000011c;
          in_stack_000000c8 = in_stack_000000a4;
          in_stack_000000cc = in_stack_000000a8;
          in_stack_000000d0 = in_stack_000000ac;
          vector_constructor_iterator_nothrow(&stack0x00000270,0x10,3,&LAB_00402d20);
          in_stack_000000a0 = in_stack_00000140;
          fVar21 = in_stack_00000094 - in_stack_00000154;
          fVar1 = in_stack_00000098 - (float)in_stack_00000158;
          fVar2 = (float)in_stack_0000009c - in_stack_0000015c;
          in_stack_00000094 =
               in_stack_00000068 * fVar2 + in_stack_00000064 * fVar1 + in_stack_00000060 * fVar21;
          in_stack_00000098 =
               in_stack_00000074 * fVar1 + in_stack_00000078 * fVar2 + in_stack_00000070 * fVar21;
          puVar9 = (undefined4 *)&stack0x00000270;
          puVar12 = &stack0x00000104;
          in_stack_00000134 = in_stack_00000094;
          for (iVar11 = 0xc; iVar11 != 0; iVar11 = iVar11 + -1) {
            *puVar12 = *puVar9;
            puVar9 = puVar9 + 1;
            puVar12 = puVar12 + 1;
          }
          in_stack_0000009c =
               (undefined4 *)
               (in_stack_00000084 * fVar1 + in_stack_00000088 * fVar2 + in_stack_00000080 * fVar21);
          in_stack_000001f0 = in_stack_000000dc;
          in_stack_000001f4 = in_stack_00000164;
          in_stack_000001b0 = in_stack_00000174;
          in_stack_000001b4 = in_stack_00000184;
          in_stack_000001c0 = in_stack_00000178;
          in_stack_000001c4 = in_stack_00000188;
          in_stack_000001b8 = in_stack_00000194;
          in_stack_000001d0 = in_stack_0000017c;
          in_stack_00000028 = &stack0x000001b0;
          in_stack_000001d4 = in_stack_0000018c;
          in_stack_000001c8 = in_stack_00000198;
          in_stack_00000024 = 0.0;
          in_stack_000001d8 = in_stack_0000019c;
          in_stack_000001dc = 0.0;
          in_stack_000001cc = 0.0;
          in_stack_000001bc = 0.0;
          in_stack_000001e8 = 0.0;
          in_stack_000001e4 = 0.0;
          in_stack_000001e0 = 0.0;
          in_stack_000001ec = 1.0;
          in_stack_00000138 = in_stack_00000098;
          in_stack_0000013c = in_stack_0000009c;
          CVertexShader__Helper_00576e0a();
          CDXEngine__Helper_00577267
                    ((int)&stack0x00000304,(int)in_stack_00000088,(int)in_stack_0000008c,
                     (int)in_stack_00000090);
          CDXEngine__Helper_00577267
                    ((int)&stack0x00000294,in_stack_000000bc,iStack000000c0,iStack000000c4);
          CVertexShader__Helper_00576e0a();
          CTexture__Helper_005768fe();
          puVar9 = (undefined4 *)&stack0x000003ec;
          puVar12 = (undefined4 *)&stack0x0000036c;
          for (iVar11 = 0x10; iVar11 != 0; iVar11 = iVar11 + -1) {
            *puVar12 = *puVar9;
            puVar9 = puVar9 + 1;
            puVar12 = puVar12 + 1;
          }
          CTexture__Helper_005768fe();
          puVar9 = (undefined4 *)&stack0x00000420;
          puVar12 = (undefined4 *)&stack0x00000320;
          for (iVar11 = 0x10; iVar11 != 0; iVar11 = iVar11 + -1) {
            *puVar12 = *puVar9;
            puVar9 = puVar9 + 1;
            puVar12 = puVar12 + 1;
          }
          CTexture__Helper_005768fe();
          iVar13 = iVar13 + 1;
          puVar12 = in_stack_0000009c + 0x10;
          iVar11 = *(int *)(in_stack_00001e6c + 0xc0);
          puVar9 = (undefined4 *)&stack0x00000394;
          for (iVar4 = 0x10; iVar4 != 0; iVar4 = iVar4 + -1) {
            *in_stack_0000009c = *puVar9;
            puVar9 = puVar9 + 1;
            in_stack_0000009c = in_stack_0000009c + 1;
          }
          in_stack_0000009c = puVar12;
        } while (iVar13 < iVar11);
      }
      if (((DAT_0063c108 == '\0') || (iVar13 = *(int *)(in_stack_00001e6c + 0xc0), 0x19 < iVar13))
         || ((DAT_00704e60 != 0 ||
             (((DAT_00704e48 != 0 && (DAT_00704e48 != 4)) || ((DAT_0089ce54 & 0x10) != 0)))))) {
        in_stack_00000054 = 0.0;
        if (0 < *(int *)(in_stack_00001e6c + 0xa8)) {
          puStack00000004 = (undefined1 *)0x0;
          do {
            pfVar15 = (float *)(puStack00000004 + *(int *)(in_stack_00001e6c + 0x134));
            pfVar8 = (float *)((int)pfVar15[8] * 0x10 + iStack000000c0);
            in_stack_00000068 = *pfVar8;
            in_stack_0000006c = (undefined4 *)pfVar8[1];
            in_stack_00000070 = pfVar8[2];
            in_stack_00000084 = pfVar15[9];
            in_stack_00000088 = pfVar15[10];
            in_stack_00000074 = *pfVar15;
            in_stack_00000078 = pfVar15[1];
            in_stack_0000007c = pfVar15[2];
            in_stack_00000080 = pfVar15[0xb];
            if (DAT_0063012c != 0xff) {
              in_stack_00000080 =
                   (float)(((int)(((uint)in_stack_00000080 >> 0x18) * DAT_0063012c) / 0xff) *
                           0x1000000 | (uint)in_stack_00000080 & 0xffffff);
            }
            if (DAT_00704e48 == 1) {
              in_stack_00000080 = (float)CDXEngine__Helper_004b52c0(pfVar15,1.0);
            }
            fVar1 = in_stack_00000070;
            puVar9 = in_stack_0000006c;
            fVar21 = in_stack_00000068;
            in_stack_00000110 = in_stack_0000007c;
            in_stack_00000108 = in_stack_00000074;
            in_stack_0000010c = in_stack_00000078;
            in_stack_00000068 = 0.0;
            in_stack_0000006c = (undefined4 *)0x0;
            in_stack_00000070 = 0.0;
            if ((DAT_0089ce54 & 0x10) == 0) {
              if (**(int **)(*(int *)(in_stack_00001e6c + 0xd8) + (int)pfVar15[8] * 4) != -1) {
                iVar13 = 0;
                do {
                  puStack00000004 =
                       &stack0x0000056c +
                       *(int *)(*(int *)(*(int *)(in_stack_00001e6c + 0xd8) + (int)pfVar15[8] * 4) +
                               iVar13) * 0x40;
                  CDXEngine__Helper_00576161();
                  CDXEngine__Helper_00576161();
                  in_stack_00000068 = in_stack_00000128 + in_stack_00000068;
                  iVar13 = iVar13 + 4;
                  in_stack_0000006c = (undefined4 *)(in_stack_0000012c + (float)in_stack_0000006c);
                  in_stack_00000070 = in_stack_00000130 + in_stack_00000070;
                  in_stack_00000074 = in_stack_000000a0 + in_stack_00000074;
                  in_stack_00000078 = in_stack_000000a4 + in_stack_00000078;
                  in_stack_0000007c = in_stack_000000a8 + in_stack_0000007c;
                } while (iVar13 < 0xc);
                in_stack_00000068 = in_stack_00000068 * _DAT_005d8608;
                in_stack_0000006c = (undefined4 *)((float)in_stack_0000006c * _DAT_005d8608);
                in_stack_00000070 = in_stack_00000070 * _DAT_005d8608;
                in_stack_000000b0 = in_stack_00000068;
                in_stack_000000b4 = in_stack_0000006c;
                in_stack_000000b8 = in_stack_00000070;
LAB_0054b520:
                fVar2 = SQRT(in_stack_0000007c * in_stack_0000007c +
                             in_stack_00000078 * in_stack_00000078 +
                             in_stack_00000074 * in_stack_00000074);
                fVar21 = in_stack_00000068;
                puVar9 = in_stack_0000006c;
                fVar1 = in_stack_00000070;
                if (fVar2 != _DAT_005d856c) {
                  fVar2 = _DAT_005d8568 / fVar2;
                  in_stack_00000074 = in_stack_00000074 * fVar2;
                  in_stack_00000078 = in_stack_00000078 * fVar2;
                  in_stack_0000007c = in_stack_0000007c * fVar2;
                }
              }
            }
            else {
              bVar3 = false;
              iVar13 = 0;
              if (0 < *(int *)(in_stack_00001e6c + 0xc0)) {
                do {
                  if (_DAT_005d856c <
                      *(float *)(*(int *)(*(int *)(in_stack_00001e6c + 0xd4) + (int)pfVar15[8] * 4)
                                + iVar13 * 4)) {
                    CDXEngine__Helper_00576161();
                    puVar12 = &stack0x0000004c;
                    CDXEngine__Helper_00576161();
                    bVar3 = true;
                    in_stack_00000050 = in_stack_00000074 * (float)puVar12 + in_stack_00000050;
                    in_stack_00000054 = in_stack_00000078 * (float)puVar12 + in_stack_00000054;
                    in_stack_00000058 = in_stack_0000007c * (float)puVar12 + in_stack_00000058;
                    fVar2 = in_stack_00000040 * (float)puVar12;
                    in_stack_0000005c = fVar2 + in_stack_0000005c;
                    in_stack_00000060 = fVar2 + in_stack_00000060;
                    in_stack_00000064 = fVar2 + in_stack_00000064;
                  }
                  iVar13 = iVar13 + 1;
                } while (iVar13 < *(int *)(in_stack_00001e6c + 0xc0));
                if (bVar3) goto LAB_0054b520;
              }
              in_stack_00000074 = in_stack_00000108;
              in_stack_00000078 = in_stack_0000010c;
              in_stack_0000007c = in_stack_00000110;
            }
            in_stack_00000070 = fVar1;
            in_stack_0000006c = puVar9;
            in_stack_00000068 = fVar21;
            fVar21 = (float)CVBufTexture__AddVertices();
            pfVar15[0x12] = fVar21;
            in_stack_00000054 = (float)((int)in_stack_00000054 + 1);
            puStack00000004 = puStack00000004 + 0x60;
          } while ((int)in_stack_00000054 < *(int *)(in_stack_00001e6c + 0xa8));
        }
        iVar13 = 0;
        if (0 < *(int *)(in_stack_00001e6c + 0xb0)) {
          do {
            CVBufTexture__AddIndices();
            iVar13 = iVar13 + 1;
          } while (iVar13 < *(int *)(in_stack_00001e6c + 0xb0));
        }
        CVBufTexture__RenderBatchList();
      }
      else {
        iVar11 = 0;
        DAT_009c68cc = iVar13;
        if (0 < *(int *)(in_stack_00001e6c + 0xc0)) {
          puVar9 = (undefined4 *)&stack0x00000554;
          puVar12 = &DAT_009c69d4;
          do {
            iVar11 = iVar11 + 1;
            puVar16 = puVar9;
            puVar17 = &stack0x000001b4;
            for (iVar13 = 0x10; iVar13 != 0; iVar13 = iVar13 + -1) {
              *puVar17 = *puVar16;
              puVar16 = puVar16 + 1;
              puVar17 = puVar17 + 1;
            }
            in_stack_00000174 = in_stack_000001b4 * _DAT_005d8608;
            puVar9 = puVar9 + 0x10;
            in_stack_00000178 = in_stack_000001b8 * _DAT_005d8608;
            in_stack_0000017c = in_stack_000001bc * _DAT_005d8608;
            in_stack_00000180 = in_stack_000001c0 * _DAT_005d8608;
            in_stack_00000184 = in_stack_000001c4 * _DAT_005d8608;
            in_stack_00000188 = in_stack_000001c8 * _DAT_005d8608;
            in_stack_0000018c = in_stack_000001cc * _DAT_005d8608;
            in_stack_00000190 = in_stack_000001d0 * _DAT_005d8608;
            in_stack_00000194 = in_stack_000001d4 * _DAT_005d8608;
            in_stack_00000198 = in_stack_000001d8 * _DAT_005d8608;
            in_stack_0000019c = in_stack_000001dc * _DAT_005d8608;
            in_stack_000001a0 = in_stack_000001e0 * _DAT_005d8608;
            in_stack_000001a4 = in_stack_000001e4 * _DAT_005d8608;
            in_stack_000001a8 = in_stack_000001e8 * _DAT_005d8608;
            in_stack_000001ac = in_stack_000001ec * _DAT_005d8608;
            in_stack_000001b0 = in_stack_000001f0 * _DAT_005d8608;
            puVar16 = &stack0x00000174;
            puVar17 = puVar12;
            for (iVar13 = 0x10; iVar13 != 0; iVar13 = iVar13 + -1) {
              *puVar17 = *puVar16;
              puVar16 = puVar16 + 1;
              puVar17 = puVar17 + 1;
            }
            puVar12 = puVar12 + 0x10;
          } while (iVar11 < *(int *)(in_stack_00001e6c + 0xc0));
        }
        CDXEngine__SetFieldE18(&DAT_009c65c0,1);
        DAT_009c68c8 = 1;
        DAT_009c690f = 1;
        CDXEngine__Helper_0054d530
                  (*(void **)(in_stack_00001e6c + 0x138),(int)piVar6,in_stack_00001e7c,
                   (uint)in_stack_00001e68);
        DAT_009c68c8 = 0;
        DAT_009c690f = 1;
        CDXEngine__SetFieldE18(&DAT_009c65c0,0);
      }
    }
    else if (((iVar13 != 4) && (iVar13 != 2)) && (iVar13 != 5)) {
      sprintf(&stack0x00000454,s_Attempt_to_render_unknown_mesh_p_00651160);
      DebugTrace(&stack0x00000454);
    }
    goto LAB_0054b7e3;
  }
  iVar13 = -1;
  if (in_stack_00001e70 != (int *)0x0) {
    iVar13 = (**(code **)(*in_stack_00001e70 + 0x1c))();
  }
  uVar10 = (uint)in_stack_00001e7c & 8;
  if (uVar10 == 8) {
    iVar13 = DAT_00704e5c;
  }
  if (((*(int *)(in_stack_00001e6c + 0xb8) < 2) ||
      (*(int *)(*(int *)(in_stack_00001e6c + 0x128) + 0x14) == 0)) ||
     ((*(int *)(in_stack_00001e6c + 0xb4) < 2 || (iVar13 < 0)))) {
    if (((DAT_00704e48 == 0) || (DAT_00704e48 == 4)) || (DAT_00704e48 == 8)) {
      CDXEngine__Helper_0054d530
                (*(void **)(in_stack_00001e6c + 0x138),(int)in_stack_00001e70,in_stack_00001e7c,
                 (uint)in_stack_00001e68);
      goto LAB_0054b7e3;
    }
    iVar11 = 0;
    iVar13 = -1;
    puStack00000004 = (undefined1 *)0x0;
    if (in_stack_00001e70 != (int *)0x0) {
      iVar13 = (**(code **)(*in_stack_00001e70 + 0x1c))();
    }
    if (uVar10 == 8) {
      iVar13 = DAT_00704e5c;
    }
    if (-1 < iVar13) {
      if (in_stack_00001e70 != (int *)0x0) {
        fVar18 = (float10)(**(code **)(*in_stack_00001e70 + 0x18))();
        puStack00000004 = (undefined1 *)(float)fVar18;
      }
      if (uVar10 == 8) {
        puStack00000004 = (undefined1 *)DAT_00704e58;
      }
      iVar11 = *(int *)(*(int *)(in_stack_00001e6c + 0x128) + 0x18);
      dVar20 = CDXEngine__Helper_0055dfe7
                         ((double)((float)*(int *)(iVar11 + 0x1c + iVar13 * 0x24) *
                                   (float)puStack00000004 +
                                  (float)*(int *)(iVar11 + iVar13 * 0x24 + 0x14)));
      iVar11 = (int)(longlong)ROUND(dVar20) % *(int *)(in_stack_00001e6c + 0xb8);
    }
    _iStack000000c0 = CONCAT44(iStack000000c4,**(undefined4 **)(in_stack_00001e6c + 0x84));
    if (DAT_00704e48 == 2) {
      if (DAT_0089ce84 == (int *)0x0) {
        DAT_0089ce84 = CTexture__FindTexture(s_meshtex_default_tga_00625498,0,0,-1,1,1);
      }
      piVar6 = (int *)CVBufTexture__GetOrCreate();
      CVBufTexture__SetVBFormat();
      CVBufTexture__SetIBFormat();
      (**(code **)(*DAT_00888a50 + 0xc0))();
      puVar9 = &DAT_009c6994;
      puVar12 = &stack0x00000174;
      for (iVar13 = 0x10; iVar13 != 0; iVar13 = iVar13 + -1) {
        *puVar12 = *puVar9;
        puVar9 = puVar9 + 1;
        puVar12 = puVar12 + 1;
      }
      puVar9 = &DAT_009c6914;
      puVar12 = (undefined4 *)&stack0x00000264;
      for (iVar13 = 0x10; iVar13 != 0; iVar13 = iVar13 + -1) {
        *puVar12 = *puVar9;
        puVar9 = puVar9 + 1;
        puVar12 = puVar12 + 1;
      }
      puVar9 = &DAT_009c6954;
      puVar12 = &stack0x000001b4;
      for (iVar13 = 0x10; iVar13 != 0; iVar13 = iVar13 + -1) {
        *puVar12 = *puVar9;
        puVar9 = puVar9 + 1;
        puVar12 = puVar12 + 1;
      }
      in_stack_00000168 = (float)(int)*(short *)(*piVar6 + 0xb0);
      in_stack_00000170 = (float)DAT_0089ce14 / (float)*(int *)(*piVar6 + 0xac);
      in_stack_0000016c = (float)DAT_0089ce14 / in_stack_00000168;
    }
    if ((DAT_00704e48 == 6) || (DAT_00704e48 == 8)) {
      CVBufTexture__GetOrCreate();
      CVBufTexture__SetVBFormat();
      CVBufTexture__SetIBFormat();
    }
    iVar13 = 6;
    iStack00000008 = 6;
    if (((DAT_00704e48 == 2) || (DAT_00704e48 == 6)) || (DAT_00704e48 == 8)) {
      iVar13 = 1;
      iStack00000008 = 1;
    }
    pfVar8 = in_stack_00001e68;
    if (DAT_00704e48 == 6) {
      in_stack_00000060 = DAT_00704e40;
      in_stack_0000005c = DAT_00704e3c;
      in_stack_00000058 = DAT_00704e38;
      in_stack_00000064 = (float)DAT_00704e44;
      fVar21 = SQRT(DAT_00704e40 * DAT_00704e40 +
                    DAT_00704e3c * DAT_00704e3c + DAT_00704e38 * DAT_00704e38);
      if (fVar21 != _DAT_005d856c) {
        fVar21 = _DAT_005d8568 / fVar21;
        in_stack_00000058 = DAT_00704e38 * fVar21;
        in_stack_0000005c = fVar21 * DAT_00704e3c;
        in_stack_00000060 = fVar21 * DAT_00704e40;
      }
      CUnitAI__Unk_0049bc80(in_stack_00001e68,&stack0x000000c8,unaff_EDI);
      fVar2 = in_stack_000000ec;
      fVar1 = in_stack_000000e8;
      fVar21 = in_stack_000000d8;
      in_stack_000000d8 = in_stack_000000cc;
      in_stack_000000cc = fVar21;
      in_stack_000000e8 = in_stack_000000d0;
      in_stack_000000d0 = fVar1;
      in_stack_000000ec = in_stack_000000e0;
      in_stack_000000e0 = fVar2;
      dVar20 = CUnitAI__Unk_0049bc40(in_stack_00001e68);
      CUnitAI__Unk_0049bbb0(&stack0x000000c8,(void *)(float)dVar20,(float)unaff_EDI);
      in_stack_0000008c =
           in_stack_00000058 * in_stack_000000c8 +
           in_stack_000000cc * in_stack_0000005c + in_stack_000000d0 * in_stack_00000060;
      in_stack_00000090 =
           in_stack_00000058 * in_stack_000000d8 +
           in_stack_000000dc * in_stack_0000005c + in_stack_000000e0 * in_stack_00000060;
      in_stack_00000060 =
           in_stack_00000058 * in_stack_000000e8 +
           in_stack_000000ec * in_stack_0000005c + in_stack_000000f0 * in_stack_00000060;
      in_stack_00000064 = in_stack_00000098;
      in_stack_00000058 = in_stack_0000008c;
      in_stack_0000005c = in_stack_00000090;
      in_stack_00000094 = in_stack_00000060;
    }
    in_stack_00000054 = 0.0;
    iVar4 = DAT_00704e48;
    if (0 < *(int *)(in_stack_00001e6c + 0xa8)) {
      iVar22 = 0;
      do {
        pfVar15 = (float *)(iVar22 + *(int *)(in_stack_00001e6c + 0x134));
        if (iVar13 != 0) {
          pfStack0000000c = pfVar15 + 0xc;
          in_stack_0000009c = (undefined4 *)iVar13;
          do {
            if ((*pfStack0000000c != -NAN) &&
               (iVar4 = DAT_00704e48,
               _DAT_005d856c <
               *(float *)(**(int **)(in_stack_00001e6c + 0x128) + 0x20 +
                         (int)*pfStack0000000c * 0x24))) {
              pfVar7 = (float *)((int)pfVar15[8] * 0x10 + iStack000000c0);
              in_stack_00000024 = *pfVar7;
              in_stack_00000028 = (undefined4 *)pfVar7[1];
              fStack0000002c = pfVar7[2];
              fVar21 = *pfVar15;
              fVar1 = pfVar15[1];
              fVar2 = pfVar15[2];
              if ((DAT_00704e48 == 6) &&
                 (in_stack_00000058 * pfVar15[4] +
                  in_stack_0000005c * pfVar15[5] + in_stack_00000060 * pfVar15[6] < _DAT_005d856c))
              {
                in_stack_000000f8 = _DAT_00704e50 * in_stack_00000058;
                in_stack_000000fc = _DAT_00704e50 * in_stack_0000005c;
                in_stack_00000024 = in_stack_00000024 - in_stack_000000f8;
                in_stack_00000028 = (undefined4 *)((float)in_stack_00000028 - in_stack_000000fc);
                fStack0000002c = fStack0000002c - _DAT_00704e50 * in_stack_00000060;
              }
              if ((DAT_00704e48 == 1) || (DAT_00704e48 == 7)) {
                in_stack_0000008c = fVar2 * pfVar8[2] + fVar21 * *pfVar8 + fVar1 * pfVar8[1];
                in_stack_00000090 = fVar1 * pfVar8[5] + fVar2 * pfVar8[6] + fVar21 * pfVar8[4];
                in_stack_00000094 = fVar1 * pfVar8[9] + fVar21 * pfVar8[8] + fVar2 * pfVar8[10];
                if (DAT_00704e48 == 7) {
                  in_stack_0000008c =
                       (float)in_stack_00000028 * pfVar8[1] +
                       in_stack_00000024 * *pfVar8 + fStack0000002c * pfVar8[2];
                  in_stack_00000098 = in_stack_000000ac;
                  in_stack_00000090 =
                       fStack0000002c * pfVar8[6] +
                       (float)in_stack_00000028 * pfVar8[5] + in_stack_00000024 * pfVar8[4];
                  in_stack_00000094 =
                       in_stack_00000024 * pfVar8[8] +
                       fStack0000002c * pfVar8[10] + (float)in_stack_00000028 * pfVar8[9];
                  in_stack_000000a0 = in_stack_0000008c;
                  in_stack_000000a4 = in_stack_00000090;
                  in_stack_000000a8 = in_stack_00000094;
                }
                fVar21 = SQRT(in_stack_0000008c * in_stack_0000008c +
                              in_stack_00000094 * in_stack_00000094 +
                              in_stack_00000090 * in_stack_00000090);
                if (fVar21 != _DAT_005d856c) {
                  fVar21 = _DAT_005d8568 / fVar21;
                  in_stack_0000008c = in_stack_0000008c * fVar21;
                  in_stack_00000090 = fVar21 * in_stack_00000090;
                  in_stack_00000094 = fVar21 * in_stack_00000094;
                }
                CDXEngine__Helper_004b52c0(&stack0x0000008c,1.0);
              }
              if (DAT_00704e48 == 2) {
                in_stack_000000b0 = in_stack_00000024;
                in_stack_000000b4 = in_stack_00000028;
                puVar23 = &stack0x00000264;
                in_stack_000000b8 = fStack0000002c;
                CDXEngine__Helper_00576297();
                in_stack_00000028 = (undefined4 *)(in_stack_00000100 / (float)puVar23);
                if ((float)in_stack_00000028 < _DAT_005d856c) {
                  in_stack_00000028 = (undefined4 *)0x0;
                }
                if ((float)in_stack_00000158 < (float)in_stack_00000028) {
                  in_stack_00000028 = in_stack_00000158;
                }
                in_stack_00000024 = (float)(DAT_00704e4c << 0x18 | 0xffffff);
              }
              fVar21 = (float)CVBufTexture__AddVertices();
              pfStack0000000c[6] = fVar21;
              iVar4 = DAT_00704e48;
            }
            pfStack0000000c = pfStack0000000c + 1;
            in_stack_0000009c = (undefined4 *)((int)in_stack_0000009c + -1);
          } while (in_stack_0000009c != (undefined4 *)0x0);
          in_stack_0000009c = (undefined4 *)0x0;
          iVar13 = iStack00000008;
        }
        in_stack_00000054 = (float)((int)in_stack_00000054 + 1);
        iVar22 = iVar22 + 0x60;
      } while ((int)in_stack_00000054 < *(int *)(in_stack_00001e6c + 0xa8));
    }
    in_stack_00000054 = 0.0;
    if (0 < *(int *)(in_stack_00001e6c + 0xb0)) {
      iVar13 = 0;
      do {
        piVar6 = (int *)(iVar13 + *(int *)(in_stack_00001e6c + 0x80));
        if (((iVar4 == 2) || (iVar4 == 6)) || (iVar4 == 8)) {
          if ((*(int *)(*piVar6 + 0x30) != -1) &&
             (_DAT_005d856c <
              *(float *)(**(int **)(in_stack_00001e6c + 0x128) + 0x20 +
                        *(int *)(*piVar6 + 0x30) * 0x24))) {
            CVBufTexture__AddIndices();
            iVar4 = DAT_00704e48;
          }
        }
        else {
          puStack00000004 = (undefined1 *)0x0;
          if (iStack00000008 != 0) {
            iVar22 = 0x30;
            do {
              if ((*(int *)(iVar22 + *piVar6) != -1) &&
                 (_DAT_005d856c <
                  *(float *)(**(int **)(in_stack_00001e6c + 0x128) + 0x20 +
                            *(int *)(iVar22 + *piVar6) * 0x24))) {
                CVBufTexture__AddIndices();
                *(undefined1 **)
                 (**(int **)(**(int **)(in_stack_00001e6c + 0x128) + 4 +
                            *(int *)(iVar22 + *piVar6) * 0x24) + 0x88) = puStack00000004;
                iVar4 = **(int **)(in_stack_00001e6c + 0x128) + *(int *)(iVar22 + *piVar6) * 0x24;
                *(undefined4 *)(**(int **)(iVar4 + 4) + 0x8c) =
                     *(undefined4 *)(*(int *)(iVar4 + 0x10) + (iVar11 % *(int *)(iVar4 + 8)) * 4);
                iVar4 = **(int **)(in_stack_00001e6c + 0x128) + *(int *)(iVar22 + *piVar6) * 0x24;
                *(undefined4 *)(**(int **)(iVar4 + 4) + 0x90) =
                     *(undefined4 *)(*(int *)(iVar4 + 0x14) + (iVar11 % *(int *)(iVar4 + 8)) * 4);
                iVar4 = **(int **)(in_stack_00001e6c + 0x128) + *(int *)(iVar22 + *piVar6) * 0x24;
                *(undefined4 *)(**(int **)(iVar4 + 4) + 0x94) =
                     *(undefined4 *)(*(int *)(iVar4 + 0x18) + (iVar11 % *(int *)(iVar4 + 8)) * 4);
                iVar4 = **(int **)(in_stack_00001e6c + 0x128) + *(int *)(iVar22 + *piVar6) * 0x24;
                *(undefined4 *)(**(int **)(iVar4 + 4) + 0x98) =
                     *(undefined4 *)(*(int *)(iVar4 + 0x1c) + (iVar11 % *(int *)(iVar4 + 8)) * 4);
              }
              puStack00000004 = (undefined1 *)((int)puStack00000004 + 1);
              iVar22 = iVar22 + 4;
              iVar4 = DAT_00704e48;
            } while ((int)puStack00000004 < iStack00000008);
          }
        }
        in_stack_00000054 = (float)((int)in_stack_00000054 + 1);
        iVar13 = iVar13 + 0xc;
      } while ((int)in_stack_00000054 < *(int *)(in_stack_00001e6c + 0xb0));
    }
    if (iVar4 == 2) {
      RenderState_Set(0x89,0);
      D3DStateCache__SetStateCached(0,1,4);
      CVBufTexture__Render();
      RenderState_Set(0x89,1);
      D3DStateCache__SetSlotMode4or5(0);
      goto LAB_0054b7e3;
    }
    if (iVar4 == 6) {
      RenderState_Set(0x89,0);
      CVBufTexture__Render();
      RenderState_Set(0x89,1);
      goto LAB_0054b7e3;
    }
    if (iVar4 == 8) {
      CVBufTexture__RenderIndexed();
      goto LAB_0054b7e3;
    }
  }
  else {
    fVar21 = 0.0;
    if (in_stack_00001e70 != (int *)0x0) {
      fVar18 = (float10)(**(code **)(*in_stack_00001e70 + 0x18))();
      fVar21 = (float)fVar18;
    }
    if (uVar10 == 8) {
      fVar21 = DAT_00704e58;
    }
    iVar11 = *(int *)(*(int *)(in_stack_00001e6c + 0x128) + 0x18);
    fVar21 = (float)*(int *)(iVar11 + iVar13 * 0x24 + 0x14) +
             (float)*(int *)(iVar11 + 0x1c + iVar13 * 0x24) * fVar21;
    if (in_stack_00001e80 != (int *)0x0) {
      (**(code **)(*in_stack_00001e80 + 0x14))();
    }
    CDXEngine__Helper_0055dfe7((double)fVar21);
    CDXEngine__Helper_0055dfe7((double)fVar21);
    fVar21 = _DAT_005d856c;
    dVar20 = (double)_DAT_005d856c;
    dVar19 = CDXEngine__Helper_0055dfe7(dVar20);
    _iStack000000c0 = (longlong)ROUND(dVar19);
    iVar11 = iStack000000c0;
    iVar13 = iStack000000c0 + 1;
    dVar19 = CDXEngine__Helper_0055dfe7(0.0);
    _iStack000000c0 = (longlong)ROUND(dVar19);
    if (iStack000000c0 < iVar13) {
      dVar19 = CDXEngine__Helper_0055dfe7(0.0);
      _iStack000000c0 = (longlong)ROUND(dVar19);
      iVar13 = iStack000000c0;
    }
    iVar11 = *(int *)(*(int *)(in_stack_00001e6c + 0x84) + iVar11 * 4);
    in_stack_0000009c = *(undefined4 **)(*(int *)(in_stack_00001e6c + 0x84) + iVar13 * 4);
    dVar20 = CDXEngine__Helper_0055dfe7(dVar20);
    fVar21 = fVar21 - (float)dVar20;
    fVar1 = _DAT_005d8568 - fVar21;
    in_stack_00000054 = 0.0;
    if (0 < *(int *)(in_stack_00001e6c + 0xa8)) {
      puStack00000004 = (undefined1 *)0x0;
      do {
        pvVar14 = (void *)((int)puStack00000004 + *(int *)(in_stack_00001e6c + 0x134));
        iVar13 = *(int *)((int)pvVar14 + 0x20);
        iVar4 = iVar13 * 0x10;
        in_stack_0000011c = fVar21 * (float)in_stack_0000009c[iVar13 * 4 + 1];
        in_stack_00000120 = fVar21 * (float)in_stack_0000009c[iVar13 * 4 + 2];
        in_stack_000000fc = fVar1 * *(float *)(iVar4 + 4 + iVar11);
        in_stack_00000100 = fVar1 * *(float *)(iVar4 + 8 + iVar11);
        in_stack_00000024 =
             fVar1 * *(float *)(iVar4 + iVar11) + fVar21 * (float)in_stack_0000009c[iVar13 * 4];
        in_stack_00000028 = (undefined4 *)(in_stack_000000fc + in_stack_0000011c);
        in_stack_00000070 = in_stack_00000100 + in_stack_00000120;
        in_stack_0000006c = in_stack_00000028;
        if (DAT_00704e48 == 1) {
          CDXEngine__Helper_004b52c0(pvVar14,1.0);
        }
        uVar5 = CVBufTexture__AddVertices();
        *(undefined4 *)((int)pvVar14 + 0x48) = uVar5;
        in_stack_00000054 = (float)((int)in_stack_00000054 + 1);
        puStack00000004 = (undefined1 *)((int)puStack00000004 + 0x60);
      } while ((int)in_stack_00000054 < *(int *)(in_stack_00001e6c + 0xa8));
    }
    iVar13 = 0;
    if (0 < *(int *)(in_stack_00001e6c + 0xb0)) {
      do {
        CVBufTexture__AddIndices();
        iVar13 = iVar13 + 1;
      } while (iVar13 < *(int *)(in_stack_00001e6c + 0xb0));
    }
  }
  CVBufTexture__RenderBatchList();
LAB_0054b7e3:
  RenderState_Set(0x1b,1);
  return;
}
