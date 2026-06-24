/* address: 0x00523b50 */
/* name: CDXEngine__GetCursorStateInRect */
/* signature: int __cdecl CDXEngine__GetCursorStateInRect(float param_1, float param_2, float param_3, float param_4) */


int __cdecl CDXEngine__GetCursorStateInRect(float param_1,float param_2,float param_3,float param_4)

{
  uint in_EAX;

  if (DAT_0089bdf4 == '\0') {
    return in_EAX & 0xffffff00;
  }
  if (DAT_00889008 == 0) {
    if ((((g_bDevModeEnabled == 0) && (param_1 <= (float)DAT_0089bda8)) &&
        ((float)DAT_0089bda8 < param_3)) &&
       ((param_2 <= (float)DAT_0089bda4 && ((float)DAT_0089bda4 < param_4)))) {
      return 1;
    }
    return 0;
  }
  return DAT_00889008 & 0xffffff00;
}
