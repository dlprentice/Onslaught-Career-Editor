/* address: 0x00562b15 */
/* name: CRT__BuildNormalizedDoubleFromParts */
/* signature: double __cdecl CRT__BuildNormalizedDoubleFromParts(int param_1, int param_2) */


double __cdecl CRT__BuildNormalizedDoubleFromParts(int param_1,int param_2)

{
  short in_stack_0000000c;
  undefined8 local_c;

  local_c = (double)CONCAT26((in_stack_0000000c + 0x3fe) * 0x10 | param_2._2_2_ & 0x800f,
                             CONCAT24((undefined2)param_2,param_1));
  return local_c;
}
