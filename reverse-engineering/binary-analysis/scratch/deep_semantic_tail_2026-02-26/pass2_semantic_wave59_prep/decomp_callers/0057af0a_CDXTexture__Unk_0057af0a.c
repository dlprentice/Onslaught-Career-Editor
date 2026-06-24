/* address: 0x0057af0a */
/* name: CDXTexture__Unk_0057af0a */
/* signature: int __stdcall CDXTexture__Unk_0057af0a(int param_1, int param_2) */


int CDXTexture__Unk_0057af0a(int param_1,int param_2)

{
  uint *puVar1;
  undefined1 *puVar2;
  int iVar3;
  int extraout_EAX;
  uint uVar4;
  int iVar5;
  undefined4 *puVar6;
  undefined4 *puVar7;
  uint *puVar8;
  undefined4 *puVar9;
  undefined *local_2a8 [2];
  undefined1 *local_2a0;
  undefined1 local_224 [64];
  undefined1 local_1e4 [4];
  undefined4 *local_1e0;
  undefined4 *local_1cc;
  undefined4 local_19c;
  uint local_174;
  uint local_170;
  int local_168;
  uint local_158;
  int *local_c;
  undefined4 *local_8;

  iVar5 = 0;
  if ((param_1 == 0) || (param_2 == 0)) {
    return -0x7fffbffb;
  }
  CFastVB__Unk_00592c50(local_2a8);
  local_2a8[0] = &DAT_0057aea4;
  local_2a0 = &DAT_0057af07;
  iVar3 = __setjmp3(local_224,0);
  if (iVar3 == 0) {
    CDXTexture__Helper_00590f80(local_1e4,0x3e,0x1d8);
    local_1cc = (undefined4 *)(*(code *)*local_1e0)(local_1e4,0,0x24);
    local_1cc[8] = param_2;
    local_1cc[2] = &DAT_0057af07;
    local_1cc[3] = &LAB_0057aedc;
    local_1cc[4] = &LAB_0057aef4;
    local_1cc[5] = CDXTexture__Helper_00592950;
    local_1cc[6] = &DAT_0057af07;
    local_1cc[1] = 0;
    *local_1cc = 0;
    local_1cc[7] = param_1;
    CMeshCollisionVolume__Unk_00591340(local_1e4,1);
    iVar3 = CDXTexture__Unk_00589116();
    if (iVar3 == 0) {
      local_19c = 1;
    }
    local_2a0 = &LAB_0057aebf;
    CDXTexture__Helper_00590ea0(local_1e4);
    if (local_168 == 1) {
      *local_c = 0x32;
      local_c[0xc] = local_174;
    }
    else {
      if (local_168 != 3) goto LAB_0057af66;
      *local_c = 0x16;
      local_c[0xc] = local_174 << 2;
    }
    local_c[3] = local_174;
    local_c[0xd] = 0;
    local_c[4] = local_170;
    local_c[5] = 1;
    if (local_c[0x10] != 0) {
      local_c[0xe] = 1;
      CFastVB__Helper_00426fd0(local_c[0xc] * local_170);
      local_c[1] = extraout_EAX;
      if ((extraout_EAX == 0) ||
         (local_8 = (undefined4 *)(*(code *)local_1e0[2])(local_1e4,1,local_174 * local_168,1),
         local_8 == (undefined4 *)0x0)) {
        iVar5 = -0x7ff8fff2;
      }
      else {
        if (*local_c == 0x32) {
          puVar6 = (undefined4 *)local_c[1];
          if (local_158 < local_170) {
            do {
              CDXTexture__Helper_00590e10(local_1e4,(int)local_8,1);
              puVar7 = (undefined4 *)*local_8;
              puVar9 = puVar6;
              for (uVar4 = local_174 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
                *puVar9 = *puVar7;
                puVar7 = puVar7 + 1;
                puVar9 = puVar9 + 1;
              }
              for (uVar4 = local_174 & 3; uVar4 != 0; uVar4 = uVar4 - 1) {
                *(undefined1 *)puVar9 = *(undefined1 *)puVar7;
                puVar7 = (undefined4 *)((int)puVar7 + 1);
                puVar9 = (undefined4 *)((int)puVar9 + 1);
              }
              puVar6 = (undefined4 *)((int)puVar6 + local_174);
            } while (local_158 < local_170);
          }
        }
        else if (*local_c == 0x16) {
          puVar8 = (uint *)local_c[1];
          while (local_158 < local_170) {
            CDXTexture__Helper_00590e10(local_1e4,(int)local_8,1);
            puVar1 = puVar8 + local_174;
            puVar2 = (undefined1 *)*local_8;
            for (; puVar8 < puVar1; puVar8 = puVar8 + 1) {
              *puVar8 = (uint)CONCAT21(CONCAT11(*puVar2,puVar2[1]),puVar2[2]);
              puVar2 = puVar2 + 3;
            }
          }
        }
        iVar5 = 0;
        CDXTexture__Unk_00591280(local_1e4);
      }
    }
  }
  else {
LAB_0057af66:
    iVar5 = -0x7fffbffb;
  }
  CFastVB__Unk_0059c610((int)local_1e4);
  return iVar5;
}
