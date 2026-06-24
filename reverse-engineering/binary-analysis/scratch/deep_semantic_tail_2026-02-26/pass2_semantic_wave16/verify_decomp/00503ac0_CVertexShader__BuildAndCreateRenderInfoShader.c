/* address: 0x00503ac0 */
/* name: CVertexShader__BuildAndCreateRenderInfoShader */
/* signature: void CVertexShader__BuildAndCreateRenderInfoShader(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CVertexShader__BuildAndCreateRenderInfoShader(void)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  int *piVar6;
  int local_270;
  char *local_26c;
  int *local_268;
  int local_264;
  int local_260;
  int local_25c [5];
  undefined4 local_248;
  undefined4 local_244;
  undefined4 local_240;
  undefined4 local_238;
  undefined4 local_234;
  undefined4 local_230;
  undefined4 local_22c;
  undefined4 local_228;
  undefined4 local_224;
  undefined4 local_220;
  undefined4 local_21c;
  undefined4 local_218;
  undefined4 local_214;
  undefined4 local_200 [4];
  undefined4 auStack_1f0 [124];

  local_200[0] = DAT_00634204;
  if (DAT_009c68c8 == '\0') {
    local_200[1] = DAT_0063424c;
  }
  else {
    local_200[1] = DAT_00634324;
  }
  if (DAT_009c68b4 == '\0') {
    local_200[2] = DAT_00634228;
  }
  else {
    local_200[2] = DAT_006342e8;
  }
  iVar3 = 3;
  if (DAT_009c73f0 != 0) {
    iVar3 = 4;
    local_200[3] = DAT_006342f4;
  }
  local_200[iVar3] = DAT_00634264;
  iVar4 = iVar3 + 1;
  if (DAT_009c68b6 != '\0') {
    local_200[iVar4] = DAT_0063430c;
    iVar4 = iVar3 + 2;
  }
  local_200[iVar4] = DAT_00634270;
  iVar3 = iVar4 + 1;
  if (DAT_009c68e8 != '\0') {
    local_200[iVar3] = DAT_00634300;
    iVar3 = iVar4 + 2;
  }
  local_260 = 4;
  local_200[iVar3] = DAT_00634210;
  iVar4 = iVar3 + 1;
  if (DAT_009c68c8 != '\0') {
    local_260 = 2;
  }
  local_270 = 0;
  if (DAT_009c68b5 == '\0') {
    if (DAT_009c68ad != '\0') {
      local_26c = &DAT_009c68a0;
      puVar2 = local_200 + iVar4;
      local_268 = &DAT_009c65c0;
      local_264 = 8;
      do {
        if (*local_26c != '\0') {
          if (local_270 < local_260) {
            local_25c[0] = 0;
            local_248 = 0;
            local_244 = 0;
            local_240 = 0;
            local_238 = 0;
            local_234 = 0;
            local_230 = 0;
            local_22c = 0;
            CDXEngine__Helper_0044a5f0();
            local_228 = 0;
            local_224 = 0;
            local_220 = 0;
            local_21c = 0;
            local_218 = 0;
            local_214 = 0;
            CDXEngine__Helper_0044a5f0();
            piVar5 = local_268;
            piVar6 = local_25c;
            for (iVar3 = 0x17; iVar3 != 0; iVar3 = iVar3 + -1) {
              *piVar6 = *piVar5;
              piVar5 = piVar5 + 1;
              piVar6 = piVar6 + 1;
            }
            uVar1 = DAT_0063418c;
            if ((local_25c[0] == 0) || (uVar1 = DAT_006341a4, local_25c[0] == 1)) {
              *puVar2 = uVar1;
              puVar2[1] = DAT_00634120;
              iVar4 = iVar4 + 2;
              puVar2 = puVar2 + 2;
              *puVar2 = DAT_00634144;
            }
            else {
              if (local_25c[0] != 2) goto LAB_00503cd3;
              *puVar2 = DAT_00634198;
            }
            iVar4 = iVar4 + 1;
            puVar2 = puVar2 + 1;
          }
LAB_00503cd3:
          local_270 = local_270 + 1;
        }
        local_26c = local_26c + 1;
        local_268 = local_268 + 0x17;
        local_264 = local_264 + -1;
      } while (local_264 != 0);
      goto LAB_00503d10;
    }
    local_200[iVar4] = DAT_00634234;
  }
  else {
    local_200[iVar4] = DAT_00634330;
  }
  iVar4 = iVar3 + 2;
LAB_00503d10:
  local_200[iVar4] = DAT_00634240;
  iVar3 = iVar4 + 1;
  if (DAT_009c68e0 != 0) {
    local_200[iVar3] = DAT_00634318;
    iVar3 = iVar4 + 2;
  }
  local_200[iVar3] = DAT_00634174;
  local_200[iVar3 + 1] = DAT_006342a0;
  local_200[iVar3 + 2] = DAT_0063427c;
  local_200[iVar3 + 3] = DAT_0063415c;
  iVar4 = iVar3 + 4;
  if (DAT_009c68b5 == '\0') {
    local_200[iVar4] = DAT_006342dc;
    iVar4 = iVar3 + 5;
  }
  local_200[iVar4] = 0;
  iVar3 = iVar4 * 4 + 4;
  if (DAT_009c73d8 != 0) {
    CVertexShader__Create
              (s_RenderInfo_shader__custom_declar_0063d0a4,0,DAT_009c73d8,local_200,iVar3,0);
    return;
  }
  CVertexShader__Create(s_RenderInfo_shader_0063d0cc,0,0,local_200,iVar3,0);
  return;
}
