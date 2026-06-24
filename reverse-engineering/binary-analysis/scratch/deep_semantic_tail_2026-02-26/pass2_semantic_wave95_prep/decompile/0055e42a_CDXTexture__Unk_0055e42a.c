/* address: 0x0055e42a */
/* name: CDXTexture__Unk_0055e42a */
/* signature: void CDXTexture__Unk_0055e42a(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__Unk_0055e42a(void)

{
  longlong lVar1;
  _FILETIME local_c;

  GetSystemTimeAsFileTime(&local_c);
  lVar1 = __allmul(local_c.dwHighDateTime,0,0,1);
  _DAT_009d0900 = lVar1 + (ulonglong)local_c.dwLowDateTime;
  return;
}
