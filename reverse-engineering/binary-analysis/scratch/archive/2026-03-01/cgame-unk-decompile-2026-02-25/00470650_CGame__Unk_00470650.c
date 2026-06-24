/* address: 0x00470650 */
/* name: CGame__Unk_00470650 */
/* signature: void __fastcall CGame__Unk_00470650(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CGame__Unk_00470650(int param_1)

{
  int *piVar1;
  short *psVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  float fVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  float fStack_208;
  int iStack_204;
  char acStack_200 [256];
  char acStack_100 [256];

  CGame__Unk_004eb1e0();
  if (*(int **)(param_1 + 0xa04) != (int *)0x0) {
    (**(code **)(**(int **)(param_1 + 0xa04) + 0xd0))();
  }
  if (*(int **)(param_1 + 0x9f8) != (int *)0x0) {
    (**(code **)(**(int **)(param_1 + 0x9f8) + 0xd0))();
  }
  fStack_208 = 110.0;
  if (DAT_00662dd0 != 0) {
    sprintf(acStack_200,s__dK__dK_of_thing_heap_free_0062c38c);
    uVar12 = 0x3f800000;
    uVar11 = 0;
    uVar10 = 0;
    psVar2 = Text__AsciiToWideScratch(acStack_200);
    uVar9 = 0xffffff00;
    uVar7 = 0x42800000;
    fVar8 = fStack_208;
    CPlatform__Font(&DAT_0088a0a8,2);
    CDXFont__DrawText(uVar7,fVar8,uVar9,psVar2,uVar10,uVar11,uVar12);
    fStack_208 = fStack_208 + _DAT_005d85cc;
    if (DAT_009c51f0 < 0x32000) {
      fStack_208 = fStack_208 + _DAT_005d85cc;
      sprintf(acStack_200,s_WARNING___THING_HEAP_NEARLY_FULL_0062c368);
      if (DAT_009c51f0 < 0x2800) {
        sprintf(acStack_200,s_ERROR___THING_HEAP_FULL__THIS_LE_0062c334);
      }
      uVar12 = 0x3f800000;
      uVar11 = 0;
      uVar10 = 0;
      psVar2 = Text__AsciiToWideScratch(acStack_200);
      uVar9 = 0xffff0000;
      uVar7 = 0x42800000;
      fVar8 = fStack_208;
      CPlatform__Font(&DAT_0088a0a8,2);
      CDXFont__DrawText(uVar7,fVar8,uVar9,psVar2,uVar10,uVar11,uVar12);
      fStack_208 = fStack_208 + _DAT_005d85cc + _DAT_005d85cc;
    }
    sprintf(acStack_200,s__dK__dK_of_default_heap_free_0062c314);
    uVar12 = 0x3f800000;
    uVar11 = 0;
    uVar10 = 0;
    psVar2 = Text__AsciiToWideScratch(acStack_200);
    uVar9 = 0xffffff00;
    uVar7 = 0x42800000;
    fVar8 = fStack_208;
    CPlatform__Font(&DAT_0088a0a8,2);
    CDXFont__DrawText(uVar7,fVar8,uVar9,psVar2,uVar10,uVar11,uVar12);
    iVar3 = DAT_009c421c;
    fStack_208 = fStack_208 + _DAT_005d85cc;
    iVar6 = DAT_009c4060 + DAT_009c422c + DAT_009c4174 + DAT_009c4178 + DAT_009c41ac;
    if (*(int *)(param_1 + 0x9f0) != 0) {
      sprintf(acStack_200,s__dK_of_mesh_data_0062c300);
      uVar12 = 0x3f800000;
      uVar11 = 0;
      uVar10 = 0;
      psVar2 = Text__AsciiToWideScratch(acStack_200);
      uVar9 = 0xffffff00;
      uVar7 = 0x42800000;
      fVar8 = fStack_208;
      CPlatform__Font(&DAT_0088a0a8,2);
      CDXFont__DrawText(uVar7,fVar8,uVar9,psVar2,uVar10,uVar11,uVar12);
      fStack_208 = fStack_208 + _DAT_005d85cc;
      sprintf(acStack_200,s__dK_of_static_shadow_data_0062c2e4);
      uVar12 = 0x3f800000;
      uVar11 = 0;
      uVar10 = 0;
      psVar2 = Text__AsciiToWideScratch(acStack_200);
      uVar9 = 0xffffff00;
      uVar7 = 0x42800000;
      fVar8 = fStack_208;
      CPlatform__Font(&DAT_0088a0a8,2);
      CDXFont__DrawText(uVar7,fVar8,uVar9,psVar2,uVar10,uVar11,uVar12);
      fStack_208 = fStack_208 + _DAT_005d85cc;
    }
    if (0x1900000 < iVar6) {
      fStack_208 = fStack_208 + _DAT_005d85cc;
      iVar6 = _rand();
      iVar6 = (iVar6 % 0xff | 0xffff00U) << 8;
      sprintf(acStack_200,s___TOO_MUCH_MESH_DATA_____dK__dK__0062c2c0);
      uVar11 = 0x3f800000;
      uVar10 = 0;
      uVar9 = 0;
      psVar2 = Text__AsciiToWideScratch(acStack_200);
      uVar7 = 0x42800000;
      fVar8 = fStack_208;
      CPlatform__Font(&DAT_0088a0a8,2);
      CDXFont__DrawText(uVar7,fVar8,iVar6,psVar2,uVar9,uVar10,uVar11);
      fStack_208 = fStack_208 + _DAT_005d85cc;
    }
    if (0x100000 < iVar3) {
      fStack_208 = fStack_208 + _DAT_005d85cc;
      iVar3 = _rand();
      iVar3 = (iVar3 % 0xff | 0xffff00U) << 8;
      sprintf(acStack_200,s___TOO_MUCH_STATIC_SHADOW_DATA_____0062c294);
      uVar11 = 0x3f800000;
      uVar10 = 0;
      uVar9 = 0;
      psVar2 = Text__AsciiToWideScratch(acStack_200);
      uVar7 = 0x42800000;
      fVar8 = fStack_208;
      CPlatform__Font(&DAT_0088a0a8,2);
      CDXFont__DrawText(uVar7,fVar8,iVar3,psVar2,uVar9,uVar10,uVar11);
      fStack_208 = fStack_208 + _DAT_005d85cc;
    }
    if (*(int *)(param_1 + 0x9f4) != 0) {
      fStack_208 = fStack_208 + _DAT_005d85cc;
      piVar4 = (int *)(param_1 + 0x3c0);
      iVar3 = 0x26c;
      do {
        piVar4[0x81] = 0;
        piVar1 = (int *)((int)&DAT_009c3df0 + iVar3);
        iVar3 = iVar3 + 4;
        piVar4[0x102] = *piVar1 - *piVar4;
        piVar4 = piVar4 + 1;
      } while (iVar3 < 0x470);
      iStack_204 = 8;
      do {
        iVar6 = 0;
        iVar3 = -1;
        iVar5 = 0;
        piVar4 = (int *)(param_1 + 0x7c8);
        do {
          if ((iVar6 < *piVar4) && (piVar4[-0x81] == 0)) {
            iVar3 = iVar5;
            iVar6 = *piVar4;
          }
          iVar5 = iVar5 + 1;
          piVar4 = piVar4 + 1;
        } while (iVar5 < 0x81);
        if (iVar3 != -1) {
          *(undefined4 *)(param_1 + 0x5c4 + iVar3 * 4) = 1;
          if (0 < *(int *)(param_1 + 0x7c8 + iVar3 * 4)) {
            sprintf(acStack_100,s__s____dK_>_dK___dK__0062c280);
            uVar12 = 0x3f800000;
            uVar11 = 0;
            uVar10 = 0;
            psVar2 = Text__AsciiToWideScratch(acStack_100);
            fVar8 = fStack_208 - _DAT_005d8ba0;
            uVar9 = 0xff000000;
            uVar7 = 0x41f00000;
            CPlatform__Font(&DAT_0088a0a8,2);
            CDXFont__DrawText(uVar7,fVar8,uVar9,psVar2,uVar10,uVar11,uVar12);
            uVar12 = 0x3f800000;
            uVar11 = 0;
            uVar10 = 0;
            psVar2 = Text__AsciiToWideScratch(acStack_100);
            uVar9 = 0xffff0000;
            uVar7 = 0x42000000;
            fVar8 = fStack_208;
            CPlatform__Font(&DAT_0088a0a8,2);
            CDXFont__DrawText(uVar7,fVar8,uVar9,psVar2,uVar10,uVar11,uVar12);
            fStack_208 = fStack_208 + _DAT_005d85cc;
          }
        }
        iStack_204 = iStack_204 + -1;
      } while (iStack_204 != 0);
    }
  }
  if (*(int *)(param_1 + 0x9f8) != 0) {
    uVar12 = 0x3f800000;
    uVar11 = 0;
    uVar10 = 0;
    psVar2 = Text__AsciiToWideScratch(s_SQUAD_INFO_0062c274);
    uVar9 = 0xffff0000;
    uVar7 = 0x40800000;
    fVar8 = fStack_208;
    CPlatform__Font(&DAT_0088a0a8,2);
    CDXFont__DrawText(uVar7,fVar8,uVar9,psVar2,uVar10,uVar11,uVar12);
    fStack_208 = fStack_208 + _DAT_005d85cc;
    (**(code **)(**(int **)(param_1 + 0x9f8) + 0xcc))(&fStack_208);
    fStack_208 = fStack_208 + _DAT_005d85cc;
  }
  if (*(int *)(param_1 + 0xa04) != 0) {
    uVar12 = 0x3f800000;
    uVar11 = 0;
    uVar10 = 0;
    psVar2 = Text__AsciiToWideScratch(s_UNIT_INFO_0062c268);
    uVar9 = 0xffff0000;
    uVar7 = 0x40800000;
    fVar8 = fStack_208;
    CPlatform__Font(&DAT_0088a0a8,2);
    CDXFont__DrawText(uVar7,fVar8,uVar9,psVar2,uVar10,uVar11,uVar12);
    fStack_208 = fStack_208 + _DAT_005d85cc;
    (**(code **)(**(int **)(param_1 + 0xa04) + 0xcc))(&fStack_208);
  }
  return;
}
