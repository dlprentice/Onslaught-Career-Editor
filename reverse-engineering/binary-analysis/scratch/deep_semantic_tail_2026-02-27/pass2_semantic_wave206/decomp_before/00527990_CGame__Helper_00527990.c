/* address: 0x00527990 */
/* name: CGame__Helper_00527990 */
/* signature: void CGame__Helper_00527990(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CGame__Helper_00527990(void)

{
  uint uVar1;
  float fVar2;
  int iVar3;
  int iVar4;
  wchar_t *pwVar5;
  uint uVar6;
  short *psVar7;
  void *this;
  int extraout_ECX;
  int iVar8;
  int iVar9;
  undefined1 *puVar10;
  int iVar11;
  float fVar12;
  float fStack00000004;
  float fStack00000008;
  float fStack0000000c;
  int iStack00000010;
  int iStack00000014;
  int in_stack_0000001c;
  int in_stack_00000020;
  int *in_stack_00001f68;
  int in_stack_00001f6c;
  int in_stack_00001f70;
  float fVar13;
  float fVar14;
  undefined4 uVar15;
  undefined1 *puVar16;
  undefined4 uVar17;
  short *text;
  undefined4 uVar18;
  int *out_extent_xy;
  undefined4 uVar19;

  CRT__AllocaProbe();
  iVar8 = 0;
  if (in_stack_00001f68 == (int *)0x0) {
    fStack0000000c = 0.0;
    iStack00000010 = 0;
    iVar4 = PLATFORM__GetWindowWidth();
    fStack00000008 = (float)PLATFORM__GetWindowHeight();
  }
  else {
    fStack0000000c = (float)in_stack_00001f68[2];
    iStack00000010 = in_stack_00001f68[3];
    iVar4 = *in_stack_00001f68;
    fStack00000008 = (float)in_stack_00001f68[1];
  }
  if (*(int *)(extraout_ECX + 8) == 1) {
    if (*(int *)(in_stack_00001f6c + 0x16c) == 0) {
      iVar11 = 0x29;
    }
    else {
      if (*(int *)(in_stack_00001f6c + 0x16c) != 1) {
        pwVar5 = CText__GetStringById(&g_Text,-0x31313163);
        goto LAB_00527a7a;
      }
      iVar11 = 0x2a;
    }
    pwVar5 = Localization__GetStringById(iVar11);
  }
  else {
    if (*(int *)(extraout_ECX + 8) != 2) {
      return;
    }
    pwVar5 = CFEPSaveGame__Helper_0046a2a0(0x6f);
    if (in_stack_00001f70 != 0) {
      uVar1 = *(uint *)(in_stack_00001f6c + 0x16c);
      uVar6 = CFrontEnd__GetPlayer0ControllerPort(0x89d758);
      if (uVar6 == uVar1) {
        pwVar5 = CFEPSaveGame__Helper_0046a2a0(0x70);
      }
      else {
        pwVar5 = CFEPSaveGame__Helper_0046a2a0(0x71);
      }
    }
  }
LAB_00527a7a:
  fStack00000004 = (float)PLATFORM__GetWindowWidth();
  puVar10 = &stack0x00000024;
  fVar12 = (float)(int)fStack00000004 * _DAT_005d8bec;
  CPlatform__Font(&DAT_0088a0a8,0);
  CFEPLanguageTest__Helper_00465a20(puVar10,pwVar5,fVar12);
  iVar11 = 0;
  psVar7 = (short *)&stack0x00000024;
  do {
    if (*psVar7 == 0) break;
    iVar11 = iVar11 + 1;
    psVar7 = psVar7 + 100;
  } while (iVar11 < 0x28);
  iStack00000014 = 0;
  fStack00000004 = (float)iVar11;
  iVar3 = iStack00000014;
  if (0 < iVar11) {
    psVar7 = (short *)&stack0x00000024;
    iVar9 = iVar11;
    do {
      out_extent_xy = &stack0x0000001c;
      text = psVar7;
      this = CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__GetTextExtent(this,text,out_extent_xy);
      if (iVar8 <= in_stack_0000001c) {
        iVar8 = in_stack_0000001c;
      }
      psVar7 = psVar7 + 100;
      iVar9 = iVar9 + -1;
      iVar3 = iVar8;
    } while (iVar9 != 0);
  }
  iStack00000014 = iVar3;
  iVar8 = iStack00000014;
  fStack0000000c = (float)iVar4 * _DAT_005d85ec + (float)(int)fStack0000000c;
  fVar12 = (float)(int)fStack00000008 * _DAT_005d85ec + (float)iStack00000010;
  if (in_stack_00001f70 != 0) {
    uVar1 = *(uint *)(in_stack_00001f6c + 0x16c);
    uVar6 = CFrontEnd__GetPlayer0ControllerPort(0x89d758);
    if (uVar6 == uVar1) {
      fVar12 = fVar12 - _DAT_005db020;
    }
    else {
      fVar12 = fVar12 + _DAT_005db020;
    }
  }
  CVBufTexture__Helper_00472e50();
  iStack00000010 = 0;
  if (0 < iVar11) {
    puVar10 = &stack0x00000024;
    fStack00000004 = (float)(int)fStack00000004 * _DAT_005d85ec;
    fVar2 = fStack0000000c - (float)(iVar8 / 2);
    fStack00000008 = fVar2;
    do {
      iVar8 = iStack00000010;
      uVar19 = 0x3f800000;
      uVar18 = 0;
      uVar17 = 0;
      uVar15 = 0xffffffff;
      fVar14 = fVar12 - (fStack00000004 - (float)iStack00000010) * (float)in_stack_00000020;
      fVar13 = fVar2;
      puVar16 = puVar10;
      CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__DrawText(fVar13,fVar14,uVar15,puVar16,uVar17,uVar18,uVar19);
      iStack00000010 = iVar8 + 1;
      puVar10 = puVar10 + 200;
    } while (iStack00000010 < iVar11);
  }
  DAT_009c690d = 1;
  DAT_009c68ac = 0;
  return;
}
