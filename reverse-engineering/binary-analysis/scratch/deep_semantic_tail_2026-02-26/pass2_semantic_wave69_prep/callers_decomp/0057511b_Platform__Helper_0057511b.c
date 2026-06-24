/* address: 0x0057511b */
/* name: Platform__Helper_0057511b */
/* signature: int Platform__Helper_0057511b(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int Platform__Helper_0057511b(void)

{
  int iVar1;
  void *extraout_EDX;
  void *extraout_EDX_00;
  void *pvVar2;
  int unaff_ESI;
  void *in_stack_00000010;
  undefined1 local_14 [16];

  CDXTexture__Unk_0058864a(local_14);
  iVar1 = CDXTexture__Unk_0058865c(local_14,in_stack_00000010,0,unaff_ESI);
  pvVar2 = extraout_EDX;
  if (-1 < iVar1) {
    iVar1 = CDXTexture__Helper_00574ae5();
    pvVar2 = extraout_EDX_00;
  }
  CDXTexture__Helper_00588896(local_14,pvVar2);
  return iVar1;
}
