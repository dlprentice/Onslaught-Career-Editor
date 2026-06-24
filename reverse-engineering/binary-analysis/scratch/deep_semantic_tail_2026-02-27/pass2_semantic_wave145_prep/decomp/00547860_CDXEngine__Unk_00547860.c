/* address: 0x00547860 */
/* name: CDXEngine__Unk_00547860 */
/* signature: int CDXEngine__Unk_00547860(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXEngine__Unk_00547860(void)

{
  int iVar1;
  void *file;
  int extraout_EAX;
  int iVar2;
  int iVar3;
  bool bVar4;
  void *unaff_retaddr;
  void *pvStack00000004;
  int in_stack_00000008;
  void *in_stack_0000000c;
  int in_stack_00000010;
  int in_stack_00000014;
  int iStack00000018;
  int iStack0000001c;
  int iStack00000020;

  CDXTexture__Helper_0055def0();
  DebugTrace(s_Building_texture_cache____00650f50);
  iStack0000001c = DAT_0089ce3c;
  sprintf(&stack0x00000024,s_ps2data_LandscapeTextureCache_te_00650f24);
  file = fopen(&stack0x00000024,&DAT_0063316c);
  pvStack00000004 = fopen(s_ps2data_LandscapeTextureCache_te_00650ef8,&DAT_0063316c);
  iVar2 = 2;
  bVar4 = false;
  do {
    if (bVar4) {
      in_stack_00000008 = 0x80;
    }
    else if (iVar2 == 3) {
      in_stack_00000008 = 0x40;
    }
    else if (iVar2 == 2) {
      in_stack_00000008 = 0x20;
    }
    iStack00000020 = iStack0000001c + (4 - iVar2) * 0x4c;
    iStack00000018 = in_stack_00000008 * in_stack_00000008;
    iVar3 = 0;
    do {
      iVar1 = iVar3 + 1;
      sprintf(&stack0x00000124,s_Shift__d_4_Line__d_64_00650ee0);
      DebugTrace(&stack0x00000124);
      in_stack_00000014 = iVar3 * 8;
      iVar3 = 0;
      do {
        CDXEngine__Unk_00541f50();
        DXPalletizer__Palletize();
        in_stack_00000010 = CDXEngine__Helper_0055feca((uint)file);
        fwrite(&stack0x00000010,4,1,pvStack00000004);
        fwrite(in_stack_0000000c,iStack00000018,1,file);
        fwrite(unaff_retaddr,0x100,4,file);
        OID__FreeObject(in_stack_0000000c);
        OID__FreeObject(unaff_retaddr);
        iVar3 = iVar3 + 8;
      } while (iVar3 < 0x200);
      iVar3 = iVar1;
    } while (iVar1 < 0x40);
    iVar2 = iVar2 + 1;
    bVar4 = iVar2 == 4;
  } while (iVar2 < 5);
  fclose(file);
  fclose(pvStack00000004);
  DebugTrace(s____done__00625304);
  return extraout_EAX;
}
