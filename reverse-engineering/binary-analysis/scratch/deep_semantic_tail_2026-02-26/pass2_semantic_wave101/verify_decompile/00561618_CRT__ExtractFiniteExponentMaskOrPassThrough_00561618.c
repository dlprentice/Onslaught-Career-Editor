/* address: 0x00561618 */
/* name: CRT__ExtractFiniteExponentMaskOrPassThrough_00561618 */
/* signature: uint __cdecl CRT__ExtractFiniteExponentMaskOrPassThrough_00561618(int param_1, uint param_2) */


uint __cdecl CRT__ExtractFiniteExponentMaskOrPassThrough_00561618(int param_1,uint param_2)

{
  if ((param_2 & 0x7ff00000) != 0x7ff00000) {
    return param_2 & 0x7ff00000;
  }
  return param_2;
}
