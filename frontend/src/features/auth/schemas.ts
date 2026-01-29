import { z } from 'zod';

/**
 * Login form validation schema.
 */
export const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email e obrigatorio')
    .email('Email invalido'),
  password: z
    .string()
    .min(1, 'Senha e obrigatoria'),
});

export type LoginFormData = z.infer<typeof loginSchema>;

/**
 * Strong password validation schema (for user creation).
 * Requirements: 8+ chars, uppercase, number, special character.
 */
export const strongPasswordSchema = z
  .string()
  .min(8, 'Senha deve ter no minimo 8 caracteres')
  .regex(/[A-Z]/, 'Senha deve conter pelo menos uma letra maiuscula')
  .regex(/[0-9]/, 'Senha deve conter pelo menos um numero')
  .regex(
    /[!@#$%^&*(),.?":{}|<>]/,
    'Senha deve conter pelo menos um caractere especial'
  );

/**
 * User creation form schema.
 */
export const createUserSchema = z.object({
  email: z.string().email('Email invalido'),
  full_name: z
    .string()
    .min(2, 'Nome deve ter no minimo 2 caracteres')
    .max(255, 'Nome muito longo'),
  password: strongPasswordSchema,
  role: z.enum(['user', 'manager', 'admin'], {
    errorMap: () => ({ message: 'Selecione um cargo valido' }),
  }),
});

export type CreateUserFormData = z.infer<typeof createUserSchema>;
