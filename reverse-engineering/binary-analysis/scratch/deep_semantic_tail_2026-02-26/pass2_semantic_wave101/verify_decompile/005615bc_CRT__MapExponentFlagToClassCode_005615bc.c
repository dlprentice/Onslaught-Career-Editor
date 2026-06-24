/* address: 0x005615bc */
/* name: CRT__MapExponentFlagToClassCode_005615bc */
/* signature: int CRT__MapExponentFlagToClassCode_005615bc(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__MapExponentFlagToClassCode_005615bc(void)

{
  uint in_EAX;

  if ((in_EAX & 0x80000) != 0) {
    return 7;
  }
  return 1;
}
